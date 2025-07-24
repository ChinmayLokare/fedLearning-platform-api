import argparse
import flwr as fl
import numpy as np

def main():
    """
    Loads model parameters from a .npz file and starts a Flower server.
    """
    parser = argparse.ArgumentParser(description="Flower Server for a Project")
    parser.add_argument(
        "--model-path",
        type=str,
        required=True,
        help="The absolute path to the .npz file containing the initial model weights."
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="The port on which the server will listen."
    )
    # The --project-id is passed but not used in this script. It's useful for logging.
    parser.add_argument("--project-id", type=str, required=True)
    args = parser.parse_args()

    print(f"--- Starting Flower Server for Project: {args.project_id} ---")

    # --- Load the initial model parameters from the specified file ---
    try:
        model_path_to_load = args.model_path
        print(f"Attempting to load model from: {model_path_to_load}")

        # np.load can handle the full path with or without the .npz extension
        npzfile = np.load(model_path_to_load)

        # Reconstruct the list of arrays in the correct order by sorting the keys
        # The keys are 'arr_0', 'arr_1', etc.
        initial_params_list = [npzfile[key] for key in sorted(npzfile.files, key=lambda x: int(x.split('_')[1]))]

        # Convert the list of numpy arrays to Flower's Parameters object
        initial_parameters = fl.common.ndarrays_to_parameters(initial_params_list)

        print("Model parameters loaded successfully.")

    except FileNotFoundError:
        print(f"ERROR: Model file not found at {args.model_path}")
        exit(1) # Exit with an error code
    except Exception as e:
        print(f"ERROR: Failed to load model parameters. Reason: {e}")
        exit(1)


    # --- Define the server strategy ---
    # We use the loaded parameters as the starting point for FedAvg.
    strategy = fl.server.strategy.FedAvg(
        fraction_fit=1.0,          # Train on 100% of available clients.
        min_fit_clients=1,           # Wait for at least 1 client before starting a training round.

        # --- THIS IS THE FIX ---
        fraction_evaluate=1.0,     # Evaluate on 100% of available clients.
        min_evaluate_clients=1,    # Only require 1 client to run an evaluation round.

        min_available_clients=1,   # Start the experiment as soon as 1 client connects.
        initial_parameters=initial_parameters,
    )

    # --- Start the Flower gRPC server ---
    print(f"Starting Flower server on 0.0.0.0:{args.port}")
    fl.server.start_server(
        server_address=f"0.0.0.0:{args.port}",
        config=fl.server.ServerConfig(num_rounds=5), # Run for many rounds
        strategy=strategy
    )

if __name__ == "__main__":
    main()