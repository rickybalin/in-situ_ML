      module ssim

      use smartredis_client, only : client_type      

      type(client_type) :: client
      integer nnDB, ppn, logging, niter, nwarmup
      real*8  t_init, t_loop
      real*8, allocatable, dimension (:) :: t_init_root
      real*8, allocatable, dimension (:) :: t_loop_root
      real*8, allocatable, dimension (:,:) :: t_data
      real*8, allocatable, dimension (:,:) :: t_data_root

      end module ssim

c ==================================================

      subroutine init_client(myrank)

      use iso_c_binding
      use ssim
      implicit none
      include "mpif.h"

      integer myrank, err
      real*8  tic, toc

c     Initialize SmartRedis clients 
      if (myrank.eq.0) write(*,*) 'Initializing SmartRedis clients ... '
      if (nnDB.eq.1) then
         tic = MPI_Wtime()
         err = client%initialize(.false.) ! NOT using a clustered database (DB on 1 node only)
         toc = MPI_Wtime()
      else
         tic = MPI_Wtime()
         err = client%initialize(.true.) ! using a clustered database (DB on multiple nodes)
         toc = MPI_Wtime()
      endif
      t_init = toc - tic
      if (err.ne.0) 
     &      stop "ERROR: client%initialize failed"


      end subroutine init_client

c ==================================================

      subroutine init_timing(myrank,nproc)

      use ssim
      implicit none
      integer myrank, nproc

      allocate(t_data(niter,2))
      if (myrank.eq.0) then
        allocate(t_init_root(nproc))
        allocate(t_loop_root(nproc))
        allocate(t_data_root(niter*nproc,2))
      endif

      end subroutine init_timing

c ==================================================

      subroutine destroy_timing(myrank)

      use ssim
      implicit none
      integer myrank

      deallocate(t_data)
      if (myrank.eq.0) deallocate(t_init_root,t_loop_root,t_data_root)

      end subroutine destroy_timing

c ==================================================

      subroutine collect_timing(myrank, nproc)

      use ssim
      implicit none
      include "mpif.h"

      integer myrank, nproc, ierr, i, n

      if (myrank.eq.0) write(*,*) "Collecting performance stats ..."
      
c     Gather data to root rank
      if (nproc.gt.1) then
         call MPI_Gather(t_init, 1, MPI_DOUBLE_PRECISION,
     &                   t_init_root, 1, MPI_DOUBLE_PRECISION,
     &                   0, MPI_COMM_WORLD, ierr)
         call MPI_Gather(t_loop, 1, MPI_DOUBLE_PRECISION,
     &                   t_loop_root, 1, MPI_DOUBLE_PRECISION,
     &                   0, MPI_COMM_WORLD, ierr)
         call MPI_Gather(t_data(:,1), niter, MPI_DOUBLE_PRECISION,
     &                   t_data_root(:,1), niter,
     &                   MPI_DOUBLE_PRECISION, 0, MPI_COMM_WORLD, ierr)
         call MPI_Gather(t_data(:,2), niter, MPI_DOUBLE_PRECISION,
     &                   t_data_root(:,2), niter,
     &                   MPI_DOUBLE_PRECISION, 0, MPI_COMM_WORLD, ierr)
      else
         t_init_root(1) = t_init
         t_loop_root(1) = t_loop
         t_data_root = t_data
      endif

c     Write data from root rank to file
      if (myrank.eq.0) then
         open(unit=10,file = "client_init.log")
         open(unit=11,file = "data_transfer.log")
         open(unit=12,file = "loop.log")
         do n=1,nproc
            write(10,*) t_init_root(n)
            write(12,*) t_loop_root(n)
            do i=1,niter
               write(11,*) t_data_root((n-1)*niter+i,1), 
     &                     t_data_root((n-1)*niter+i,2)
            enddo
         enddo
         close(10)
         close(11)
         close(12)
      endif

      end subroutine collect_timing

c ==================================================

      program  clientFtn

      use iso_c_binding
      use fortran_c_interop
      use ssim
      use, intrinsic :: iso_fortran_env
      implicit none
      include "mpif.h"

      real*8, allocatable, dimension (:,:,:) :: send_data
      real*8, allocatable, dimension (:,:,:) :: rcv_data
      real*8, allocatable, dimension (:) :: read_inputs
      real*8 x, tic, toc, tic_loop, toc_loop
      integer nx, ny, nz, seed, num_inputs
      integer its, i, j, k, err
      integer myrank, comm_size, ierr, status(MPI_STATUS_SIZE), 
     &        nproc, name_len
      character*255 key
      logical exlog
      character*(MPI_MAX_PROCESSOR_NAME) proc_name

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
         nnDB = int(read_inputs(1))
         ppn = int(read_inputs(2))
         logging = int(read_inputs(3))
         read(24,*) (read_inputs(j), j=1,num_inputs)
         nx = int(read_inputs(1))
         ny = int(read_inputs(2))
         nz = int(read_inputs(3))
         close(24)
         deallocate(read_inputs)
      else
         if (myrank.eq.0) then
            write(*,*) 'Inputs not specified in input.config'
            write(*,*) 'Setting nnDB=1, ppn=1, and logging=0'
         endif
         nnDB = 1
         ppn = 1
         logging = 0
         nx = 8; ny = 8; nz = 8
      endif

c     Initialize SmartRedis client and timing arrays
      niter = 40
      nwarmup = 2
      if (logging.eq.1) call init_timing(myrank,nproc)
      call init_client(myrank)
      call MPI_Barrier(MPI_COMM_WORLD,ierr)
      if (myrank.eq.0) write(*,*) 'All SmartRedis clients initialized'

c     Create data to be send to database
      allocate(send_data(nx,ny,nz))
      allocate(rcv_data(nx,ny,nz))
      seed = myrank+1
      call RANDOM_SEED(seed)


c     Generate the key for the data
c     The key will be tagged with the rank ID
      key = "y."
      write (key, "(A2,I0)") trim(key), myrank

c     Generate the transfer data
      do i=1,nx
         do j=1,ny
            do k=1,nz
               call RANDOM_NUMBER(x)
               send_data(i,j,k) = x
            enddo
         enddo
      enddo

c     Do a small warmup loop
      do its=1,nwarmup
         ! Sleep for a little to separate out inference requests
         call sleep(2)
  
         ! Send data
         err = client%put_tensor(trim(key), send_data, 
     &                          shape(send_data))
         if (err.ne.0) 
     &      stop "ERROR: client%put_tensor failed"

         ! Retreive data
         err = client%unpack_tensor(trim(key), rcv_data,
     &                             shape(rcv_data))
         if (err.ne.0) 
     &      stop "ERROR: client%unpack_tensor failed"
         call MPI_Barrier(MPI_COMM_WORLD,ierr)

      enddo

c     Start a do loop and perform send and receive data transfers
      tic_loop = MPI_Wtime()
      do its=1,niter
         ! Sleep for a little to separate out inference requests
         call sleep(2)

         ! Send the data
!d         if (myrank.eq.0) write(*,*) 
!d     &            'Sending data to database with key ',
!d     &            trim(key), ' and shape ',
!d     &            shape(send_data)
         tic = MPI_Wtime()
         err = client%put_tensor(trim(key), send_data, 
     &                          shape(send_data))
         toc = MPI_Wtime()
         if (err.ne.0) 
     &      stop "ERROR: client%put_tensor failed"
         call MPI_Barrier(MPI_COMM_WORLD,ierr)
!d         if (myrank.eq.0) write(*,*) 'Finished sending inference data'
         t_data(its,1) = toc - tic

         ! Retreive the data
         tic = MPI_Wtime()
         err = client%unpack_tensor(trim(key), rcv_data,
     &                             shape(rcv_data))
         toc = MPI_Wtime()
         if (err.ne.0) 
     &      stop "ERROR: client%unpack_tensor failed"
         call MPI_Barrier(MPI_COMM_WORLD,ierr)
!d         if (myrank.eq.0) write(*,*) 'Finished retreiving predictions'
         t_data(its,2) = toc - tic

      enddo
      toc_loop = MPI_Wtime()
      t_loop = toc_loop - tic_loop

c     Collect and write timing statistics
      if (logging.eq.1) call collect_timing(myrank,nproc)

c     Finilization
      if (myrank.eq.0) write(*,*) "Exiting ... "
      deallocate(send_data)
      deallocate(rcv_data)
      if (logging.eq.1) call destroy_timing(myrank)
      call MPI_FINALIZE(ierr)

      end program clientFtn
