
module inference_cpp_bridge

  use iso_c_binding, only : c_ptr, c_float, c_int, c_loc

  implicit none; private

  interface
    subroutine torch_inf_c(model_ptr, myGPU, batch, channels, pixels, inputs, outputs) bind(c, name="torch_inf")
        use iso_c_binding, only : c_int, c_float, c_ptr
        type(c_ptr), value,  intent(in) :: model_ptr !< Pointer to the model
        integer(kind=c_int), intent(in) :: myGPU !< Local GPU ID for this rank
        integer(kind=c_int), intent(in) :: batch !< Batch size of images
        integer(kind=c_int), intent(in) :: channels !< Number of channels in images
        integer(kind=c_int), intent(in) :: pixels !< Number of pixels in each dimension in images
        type(c_ptr), value,  intent(in) :: inputs !< void*-like pointer to input tensor
        type(c_ptr), value,  intent(in) :: outputs !< void*-like pointer to output tensor
    end subroutine torch_inf_c
  end interface

  interface
    subroutine upload_model(model_ptr, myGPU) bind(c, name="upload_model")
      use iso_c_binding, only : c_ptr, c_int
      type(c_ptr), intent(out) :: model_ptr !< Hold the pointer to a loaded model
      integer(kind=c_int), intent(in) :: myGPU !< Local GPU ID for this rank
    end subroutine upload_model
  end interface

  public :: torch_inf, upload_model

  contains

  !> Callout to torch for inference. Note all the C-Fortran conversion are done here
  subroutine torch_inf(model,myGPU,batch,channels,pixels,inputs,outputs)
    type(c_ptr),                           intent(in   ) :: model !< Loaded model
    integer(kind=c_int),                   intent(in   ) :: myGPU !< Local GPU ID for this rank
    integer(kind=c_int),                   intent(in   ) :: batch !< Batch size of images
    integer(kind=c_int),                   intent(in   ) :: channels !< Number of channels in images
    integer(kind=c_int),                   intent(in   ) :: pixels !< Number of pixels in each dimension 
    real(kind=c_float), dimension(batch,channels,pixels,pixels), intent(in   ) :: inputs !< void*-like pointer to input tensor
    real(kind=c_float), dimension(batch,1000), intent(  out) :: outputs !< void*-like pointer to output tensor

    real(kind=c_float), dimension(pixels,pixels,channels,batch), target :: c_inputs
    real(kind=c_float), dimension(1000,batch), target :: c_outputs
    type(c_ptr) :: inputs_ptr, outputs_ptr
    integer :: i, j, k, l

    ! Change from column major (Fortran) to row major (C++)
    !c_inputs = transpose(inputs)
    do i=1,batch
    do j=1,channels
    do k=1,pixels
    do l=1,pixels
        c_inputs(l,k,j,i) = inputs(i,j,k,l)
    enddo;enddo;enddo;enddo

    ! Create void*-like pointers to the array memory
    inputs_ptr = c_loc(c_inputs)
    outputs_ptr = c_loc(c_outputs)

    call torch_inf_c(model, myGPU, batch, channels, pixels, inputs_ptr, outputs_ptr)

    ! Change from row major to column major
    outputs = transpose(c_outputs)

  end subroutine torch_inf

end module inference_cpp_bridge
