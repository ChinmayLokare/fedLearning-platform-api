package com.federated.fl_platform_api.repository;

import com.federated.fl_platform_api.model.Project;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface ProjectRepository extends JpaRepository<Project, UUID> {
}
