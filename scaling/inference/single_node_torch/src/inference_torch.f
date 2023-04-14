      module timing

      integer logging, niter, ppn, nGPU
      real*8  t_init
      real*8, allocatable, dimension (:) :: t_init_root
      real*8, allocatable, dimension (:) :: t_data
      real*8, allocatable, dimension (:) :: t_data_root

      end module timing

c ==================================================

      subroutine init_timing(myrank,nproc)

      use timing
      implicit none
      integer myrank, nproc

      allocate(t_data(niter-2))
      if (myrank.eq.0) then
        allocate(t_init_root(nproc))
        allocate(t_data_root((niter-2)*nproc))
      endif

      end subroutine init_timing

c ==================================================

      subroutine destroy_timing(myrank)

      use timing
      implicit none
      integer myrank

      deallocate(t_data)
      if (myrank.eq.0) deallocate(t_init_root,t_data_root)

      end subroutine destroy_timing

c ==================================================

      subroutine collect_timing(myrank, nproc)

      use timing
      use mpi
      implicit none

      integer myrank, nproc, ierr, i, n

      if (myrank.eq.0) write(*,*) "Collecting performance stats ..."

c     Gather data to root rank
      if (nproc.gt.1) then
         call MPI_Gather(t_init, 1, MPI_DOUBLE_PRECISION,
     &                   t_init_root, 1, MPI_DOUBLE_PRECISION,
     &                   0, MPI_COMM_WORLD, ierr)
         call MPI_Gather(t_data, (niter-2), MPI_DOUBLE_PRECISION,
     &                   t_data_root, (niter-2), MPI_DOUBLE_PRECISION,
     &                   0, MPI_COMM_WORLD, ierr)
      else
         t_init_root(1) = t_init
         t_data_root = t_data
      endif

c     Write data from root rank to file
      if (myrank.eq.0) then
         open(unit=10,file = "client_init.log")
         open(unit=11,file = "data_transfer.log")
         do n=1,nproc
            write(10,*) t_init_root(n)
            do i=1,niter-2
               write(11,*) t_data_root((n-1)*(niter-2)+i)
            enddo
         enddo
         close(10)
         close(11)
      endif

      end subroutine collect_timing

c ==================================================

      program  clientFtn

      use iso_c_binding
      use inference_cpp_bridge
      use timing
      use, intrinsic :: iso_fortran_env
      use mpi
      implicit none

      real(kind=c_float), allocatable, dimension (:,:,:,:) :: inputs
      real(kind=c_float), allocatable, dimension (:,:) :: outputs
      real*8, allocatable, dimension (:) :: read_inputs
      real*4 x
      real*8 tic, toc
      integer batch, channels, pixels, seed, num_inputs
      integer its, i, j, k, myrankl, myGPUl
      integer myrank, comm_size, ierr, status(MPI_STATUS_SIZE),
     &        nproc, name_len
      logical*1 exlog
      character*(MPI_MAX_PROCESSOR_NAME) proc_name
      type(c_ptr) :: model

c     Initialize MPI
      call MPI_INIT(ierr)
      call MPI_COMM_SIZE(MPI_COMM_WORLD, comm_size, ierr)
      call MPI_COMM_RANK(MPI_COMM_WORLD, myrank, ierr)
      call MPI_Get_processor_name( proc_name, name_len, ierr)
      nproc = comm_size
!d      write(*,100) 'Hello from rank ',myrank,'/',nproc,
!d     &           ' on node ',trim(proc_name)
!d100   format (A,I0,A,I0,A,A)
      call MPI_Barrier(MPI_COMM_WORLD,ierr)
      flush(OUTPUT_UNIT)

c     Read config parameters
      inquire(file='input.config',exist=exlog)
      if(exlog) then
         open (unit=24, file='input.config', status='unknown')
         read(24,*) num_inputs
         allocate(read_inputs(num_inputs))
         read(24,*) (read_inputs(j), j=1,num_inputs)
         ppn = int(read_inputs(1))
         nGPU = int(read_inputs(2))
         logging = int(read_inputs(3))
         read(24,*) (read_inputs(j), j=1,num_inputs)
         batch = int(read_inputs(1))
         channels = int(read_inputs(2))
         pixels = int(read_inputs(3))
         close(24)
         deallocate(read_inputs)
      else
         if (myrank.eq.0) then
            write(*,*) 'Inputs not specified in input.config'
            write(*,*) 'Setting ppn=1, nGPU=1, logging=0'
            write(*,*) 'Setting input size to (1,3,224,224)'
         endif
         ppn = 1
         nGPU = 1
         logging = 0
         batch = 1
         channels = 3
         pixels = 224
      endif

c     Initialize timing arrays and upload model
      niter = 42
      myrankl = mod(myrank,ppn)
      myGPUl = myrank/(ppn/nGPU)
!d      write(*,*) myrank, ': is local rank ',myrankl,
!d    &           'and will work with local GPU', myGPUl
      if (logging.eq.1) call init_timing(myrank,nproc)
      call upload_model(model,myGPUl)
      call MPI_Barrier(MPI_COMM_WORLD,ierr)
      if (myrank.eq.0) write(*,*) 'All ranks uploaded model'

c     Allocate input and output data for the model
      allocate(inputs(batch,channels,pixels,pixels))
      allocate(outputs(batch,1000))
      seed = myrank+1
      call RANDOM_SEED(seed)


c     Generate the transfer data
      do i=1,channels
         do j=1,pixels
            do k=1,pixels
               call RANDOM_NUMBER(x)
               inputs(:,i,j,k) = x
            enddo
         enddo
      enddo
!d      if (myrank.eq.0) write(*,*) 'Created input array of size ', 
!d     &                            shape(inputs)

c     Start a do loop and perform inference
      do its=1,niter
         ! Sleep for a little to separate out inference requests
         call sleep(2)

         ! Perform inference
         tic = MPI_Wtime()
         call torch_inf(model,myGPUl,batch,channels,pixels,
     &                  inputs,outputs)
         toc = MPI_Wtime()
         call MPI_Barrier(MPI_COMM_WORLD,ierr)
!d         if (myrank.eq.0) write(*,*) 'All ranks performed inference',
!d     &                    ' for time step ', its
         if (its.gt.2) t_data(its-2) = toc - tic

      enddo

c     Collect and write timing statistics
      if (logging.eq.1) call collect_timing(myrank,nproc)

c     Finilization
      if (myrank.eq.0) write(*,*) "Exiting ... "
      if (logging.eq.1) call destroy_timing(myrank)
      call MPI_FINALIZE(ierr)

      end program clientFtn
