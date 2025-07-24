package com.federated.fl_platform_api.service;

import com.federated.fl_platform_api.dto.CreateProjectRequest;
import com.federated.fl_platform_api.model.Project;
import com.federated.fl_platform_api.repository.ProjectRepository;
import com.federated.fl_platform_api.flower.FlowerServerManager;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.IOException;
import java.util.Optional;
import java.util.UUID;

@Service
public class ProjectService {

    @Autowired
    private ProjectRepository projectRepository;
    @Autowired
    private FlowerServerManager flowerServerManager;
    @Autowired
    private ModelInitializer modelInitializer;

    public Project createProject(CreateProjectRequest request) throws IOException, InterruptedException {
        System.out.println("\n\n==================== NEW PROJECT REQUEST RECEIVED ====================");
        System.out.println("=> Project Name: " + request.getName());
        System.out.println("=> Model Type: " + request.getModelType());

        // --- Step 1: Initial Database Entry ---
        System.out.println("\n[1/3] Persisting initial project state to database...");
        Project project = new Project();
        project.setName(request.getName());
        project.setModelType(request.getModelType());
        Project savedProject = projectRepository.save(project);
        System.out.println("...Success! Project ID: " + savedProject.getId());

        // --- Step 2: Model Initialization (The "Loader" Part) ---
        File modelFile = new File("models/" + savedProject.getId().toString() + ".npz");
        String absoluteModelPath = modelFile.getAbsolutePath();
        savedProject.setModelPath(absoluteModelPath);

        System.out.println("\n[2/3] Initializing model file... (This may take a moment)");
        System.out.println("------------------------- LOADER START -------------------------");

        // This is the long-running, blocking call.
        modelInitializer.initializeModelFile(request.getModelType(), absoluteModelPath, request.getPretrainEpochs());

        System.out.println("-------------------------- LOADER END --------------------------");
        System.out.println("...Success! Model file created at: " + absoluteModelPath);

//        // --- Step 3: Start Federated Learning Server ---
//        System.out.println("\n[3/4] Starting dedicated Flower server process...");
//        int port = flowerServerManager.startServerForProject(savedProject,false);
//        savedProject.setServerPort(port);
//        System.out.println("...Success! Flower server started on port: " + port);

        // --- Step 3: Final Database Update ---
        System.out.println("\n[3/3] Updating project with server details...");
        Project finalProject = projectRepository.save(savedProject);
        System.out.println("...Success! Project is fully configured and ready.");
        System.out.println("==================== PROJECT CREATION COMPLETE ====================\n");

        return finalProject;
    }

    public Project startServerForProject(UUID projectId) throws IOException, InterruptedException {

        Optional<Project> savedProject = projectRepository.findById(projectId);
        System.out.println("\n[2/4] Finding project with ID: " + projectId);

        Project project = projectRepository.findById(projectId).orElseThrow(() -> new RuntimeException("Project not found with ID: " + projectId));

        // Check if server is already running for this project

        if(flowerServerManager.isServerRunning(projectId)){
            System.out.println("...Server is already running for this project on port: " + project.getServerPort());
            return project;
        }

        System.out.println("\n[2/4] Starting dedicated Flower server process...");

        int port = flowerServerManager.startServerForProject(project,true);
        project.setServerPort(port);

        System.out.println("...Success! Flower server started on port: " + port);

        System.out.println("\n[3/4] Updating project with server details...");
        Project finalProject = projectRepository.save(project);

        System.out.println("...Success! Project is fully configured and ready.");
        System.out.println("\n[4/4] Starting dedicated Flower server process...");
        return finalProject;

    }
}