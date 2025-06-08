package com.federated.fl_platform_api.controller;

import com.federated.fl_platform_api.dto.LoginRequest;
import com.federated.fl_platform_api.dto.RegisterRequest;
import com.federated.fl_platform_api.exception.UserAlreadyExistsException;
import com.federated.fl_platform_api.model.User;
import com.federated.fl_platform_api.security.JwtTokenProvider;
import com.federated.fl_platform_api.service.UserService;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;
import org.springframework.security.core.AuthenticationException;

import java.util.HashMap;
import java.util.Map;
import com.federated.fl_platform_api.security.JwtTokenProvider;
import org.springframework.security.core.userdetails.UserDetails;

@RestController
@RequestMapping("/api/auth")
// @CrossOrigin(origins = "*") // Keep if you don't have global WebConfig, remove if you do
public class AuthController {

    private final UserService userService;
    private final AuthenticationManager authenticationManager;
    private final JwtTokenProvider tokenProvider;


    @Autowired
    public AuthController(UserService userService, AuthenticationManager authenticationManager, JwtTokenProvider tokenProvider) {
        this.userService = userService;
        this.authenticationManager = authenticationManager;
        this.tokenProvider = tokenProvider;
    }

    @PostMapping("/register")
    public ResponseEntity<?> registerUser(@Valid @RequestBody RegisterRequest registerRequest) {
        try {
            User newUser = new User();
            newUser.setUsername(registerRequest.getUsername());
            newUser.setEmail(registerRequest.getEmail());
            newUser.setPassword(registerRequest.getPassword());

            User registeredUser = userService.registerUser(newUser);

            // Return a structured JSON response
            Map<String, Object> responseBody = Map.of(
                    "message", "User registered successfully!",
                    "userId", registeredUser.getId() // Or any other relevant info
            );
            return ResponseEntity.status(HttpStatus.CREATED).contentType(MediaType.APPLICATION_JSON).body(responseBody);

        } catch (UserAlreadyExistsException e) {
            // Return error as JSON too for consistency
            Map<String, String> errorBody = Map.of("error", e.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).contentType(MediaType.APPLICATION_JSON).body(errorBody);
        } catch (Exception e) {
            e.printStackTrace(); // Good to log the full stack trace for unexpected errors
            Map<String, String> errorBody = Map.of("error", "An unexpected error occurred. Please try again.");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).contentType(MediaType.APPLICATION_JSON).body(errorBody);
        }
    }

    @PostMapping("/login")
    public ResponseEntity<?> authenticateUser(@Valid @RequestBody LoginRequest loginRequest) {
        try {
            Authentication authentication = authenticationManager.authenticate(
                    new UsernamePasswordAuthenticationToken(
                            loginRequest.getUsername(),
                            loginRequest.getPassword()
                    )
            );

            SecurityContextHolder.getContext().setAuthentication(authentication);
            // User is authenticated.
            // Generate JWT token
            String jwt = tokenProvider.generateToken(authentication);


            String username;
            Object principal = authentication.getPrincipal();
            if (principal instanceof UserDetails) {
                username = ((UserDetails) principal).getUsername();
            } else {
                username = principal.toString(); // Fallback
            }

            // Create response body with token and username
            Map<String, Object> responseBody = new HashMap<>();
            responseBody.put("accessToken", jwt);
            responseBody.put("tokenType", "Bearer");
            responseBody.put("username", username);

            return ResponseEntity.ok(responseBody);

        } catch (AuthenticationException e) {
            // Authentication failed (e.g., bad credentials)
            Map<String, String> errorBody = Map.of("error", "Login failed: Invalid username or password.");
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).contentType(MediaType.APPLICATION_JSON).body(errorBody);
        }
    }




}