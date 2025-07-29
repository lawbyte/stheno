<p align="center">
  <img src="https://github.com/Ch0pin/stheno/assets/4659186/0c82c3da-1a89-43b5-9b8f-4c161dfc5c5c" alt="Stheno">
</p>

# Stheno

## Overview

**Stheno (Σθεννώ)** is a powerful tool designed for analyzing and manipulating intents in Android applications. Named after the sister of Medusa, Stheno is indeed a sub project of [Medusa](https://github.com/Ch0pin/medusa) that brings formidable capabilities akin to Burp Suite but tailored specifically for intents. This tool is essential for Android penetration testers, developers, and security enthusiasts who seek to understand and secure their applications against intent-based vulnerabilities.

## Features

- **Intent Interception**: Capture and inspect intents sent and received by Android applications. 
- **Intent Modification (TODO)**: Modify intercepted intents to test how applications handle unexpected or malformed data.
- **Intent Replay (TODO)**: Resend captured intents to test the stability and security of applications.
- **Logging and Reporting (TODO)**: Detailed logging of all activities and comprehensive reporting to aid in vulnerability assessment.

  
<p align="center">
  <img src="https://github.com/Ch0pin/stheno/assets/4659186/fd49c39e-865b-4dc3-b2d1-59a0f4594028" alt="monitor">
</p>

## Installation 

Stheno can be used either as a standalone tool or in conjunction with [Medusa](https://github.com/Ch0pin/medusa).

### Standalone installation:

1. **Install the Requirements:**
   ```sh
   pip install -r requirements.txt
   ```

2. **Build the Project:**
   Navigate to the `Intent-monitor` folder and run:
   ```sh
   ./gradlew build
   ```

3. **Run the Application:**
   
   **Option A: Using Gradle (Recommended)**
   ```sh
   ./gradlew run
   ```
   
   **Option B: Using the JAR file**
   ```sh
   # Build the fat JAR with all dependencies
   ./gradlew fatJar
   
   # Run the JAR (requires JavaFX to be installed)
   java --module-path /usr/share/openjfx/lib --add-modules javafx.controls,javafx.fxml,javafx.web -jar build/libs/Intent-monitor-fat.jar
   ```
   
   **Option C: Using custom runtime (includes JavaFX)**
   ```sh
   # Create custom runtime with JavaFX included
   ./gradlew jlink
   
   # Run the custom runtime
   ./build/image/bin/Stheno
   ```

### Using with Medusa:

If you are using Stheno with Medusa, only step 2 is necessary:

1. **Build the Project:**
   Navigate to the `Intent-monitor` folder and run:
   ```sh
   ./gradlew build
   ```

2. **Run the Application:**
   Use any of the methods described in step 3 above.
---

## Basic Usage:

1. Run the python script defining the target app that you want to monitor (e.g. `python3 stheno.py -t com.foo.bar`)
2. Run the monitor and go to menu->start to start monitoring the intents

## Troubleshooting

### JavaFX Issues
If you encounter "JavaFX runtime components are missing" error:

1. **Install JavaFX:**
   ```sh
   sudo apt update
   sudo apt install openjfx libopenjfx-java
   ```

2. **Use the custom runtime (recommended):**
   ```sh
   ./gradlew jlink
   ./build/image/bin/Stheno
   ```

### Module Resolution Issues
If you encounter module resolution errors:

1. **Use Gradle run (simplest):**
   ```sh
   ./gradlew run
   ```

2. **Or use the custom runtime:**
   ```sh
   ./gradlew jlink
   ./build/image/bin/Stheno
   ```

### Build Issues
If the build fails:

1. **Clean and rebuild:**
   ```sh
   ./gradlew clean
   ./gradlew build
   ```

2. **Check Java version:**
   ```sh
   java -version
   ```
   Ensure you're using Java 17 or higher.


## Contributing

We welcome contributions from the community! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Implement your changes and test thoroughly.
4. Submit a pull request with a detailed description of your changes.
