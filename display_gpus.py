import torch

def display_available_gpu_devices():
    # Get the number of available GPU devices
    num_devices = torch.cuda.device_count()

    if num_devices == 0:
        print("No GPU devices found.")
    else:
        print(f"Number of available GPU devices: {num_devices}")

        # List all available GPU devices and their names
        for device_id in range(num_devices):
            device_name = torch.cuda.get_device_name(device_id)
            print(f"GPU Device {device_id}: {device_name}")
            device = torch.device("cuda")
            num_cuda_cores = torch.cuda.get_device_properties(device)
            print(f"Properties: {num_cuda_cores}")

if __name__ == "__main__":
    display_available_gpu_devices()