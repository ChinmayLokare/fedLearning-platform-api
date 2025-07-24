package com.federated.fl_platform_api.controller;


import com.federated.fl_platform_api.dto.CreateProjectRequest;
import com.federated.fl_platform_api.model.Project;
import com.federated.fl_platform_api.service.ProjectService;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;
import java.util.UUID;

@RestController
@RequestMapping("/api/projects")
public class ProjectController {

    @Autowired
    private ProjectService projectService;

    @PostMapping
    public ResponseEntity<Project> createProject(@Valid @RequestBody CreateProjectRequest request) {
        try {
            Project newProject = projectService.createProject(request);
            return ResponseEntity.ok(newProject);
        } catch (Exception e) {
            // It's better to have a proper exception handler, but for now this is ok
            return ResponseEntity.badRequest().build();
        }
    }

    @GetMapping("/{projectId}/start")
    public ResponseEntity<Project> startProjectServer(@PathVariable UUID projectId) {

        try{
            Project startedProject = projectService.startServerForProject(projectId);
            return ResponseEntity.ok(startedProject);
        }catch (RuntimeException e){
            return ResponseEntity.badRequest().build();
        }catch (Exception e){
            return ResponseEntity.internalServerError().build();
        }

    }



}
