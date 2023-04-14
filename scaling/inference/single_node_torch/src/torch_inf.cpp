#include <torch/script.h>
#include <iostream>
#include <memory>

extern "C" {

void upload_model(void** model_ptr, int *myGPU) {

  std::string model_name = "./resnet50_jit.pt";
  try {
    //std::cout << "loading the model " << model_name << "\n" << std::flush;
    auto model_tmp = torch::jit::load(model_name);
    torch::jit::Module* model = new torch::jit::Module(model_tmp);
    model->to(torch::Device(torch::kCUDA, *myGPU));
    std::cout << "loaded the model to GPU:" << *myGPU << "\n" << std::flush;
    *model_ptr = NULL;
    *model_ptr = reinterpret_cast<void*>(model);
    //printf("%p\n", model);
  }
  catch (const c10::Error& e) {
    std::cerr << "error loading the model\n" << std::flush;
  }

}

void torch_inf(void *model_ptr, int *myGPU, int *batch, int *channels, int *pixels, void *inputs, void *outputs) {

  // Convert input array to Torch tensor
  //auto options = torch::TensorOptions()
  //                     .dtype(torch::kFloat32)
  //                     .device(torch::kCUDA,myGPU);
  //torch::Tensor input_tensor = torch::from_blob(inputs, {*batch,*channels,*pixels,*pixels}, options);
  torch::Tensor input_tensor = torch::from_blob(inputs, {*batch,*channels,*pixels,*pixels}, torch::dtype(torch::kFloat32));
  input_tensor = input_tensor.to(torch::Device(torch::kCUDA, *myGPU));
  //std::cout << "created the input vector\n" << std::flush;

  // Convert Tensor to vector
  //std::vector<torch::jit::IValue> model_inputs;
  //model_inputs.push_back(input_tensor);
  //std::cout << "prepared input vector for inference\n";

  // Perform inference
  torch::jit::Module* module = reinterpret_cast<torch::jit::Module*>(model_ptr);
  //torch::Tensor output_tensor = module->forward(model_inputs).toTensor();
  torch::Tensor output_tensor = module->forward({input_tensor}).toTensor();
  //std::cout << "performed inference\n" << std::flush;

  // Extract predictions
  outputs = (void *) output_tensor.data_ptr<float>();

}


}

