# ParkNova: Smart Parking Management System

ParkNova is a modern, full-stack parking management solution built with **Java (Spring Boot 3)**, **MySQL**, and **Tailwind CSS**. It provides a premium experience for both users and administrators to manage parking slots in real-time.

## 🚀 Features

- **Role-Based Authentication**: Secure login for ADMIN and USER roles.
- **Real-Time Parking Grid**: Color-coded slot availability (Green = Available, Red = Occupied).
- **Smart Booking**: One-click booking with automatic fee calculation upon checkout.
- **QR Code Generation**: Unique QR codes for every booking for easy entry/exit scanning.
- **Admin Dashboard**: Comprehensive analytics including occupancy rates, total slots, and revenue tracking.
- **Responsive Design**: Premium UI with Glassmorphism, Dark/Light mode support, and smooth animations.
- **Data Persistence**: Robust MySQL backend using Spring Data JPA.

## 🛠️ Technology Stack

- **Backend**: Spring Boot 3.2.4, Spring Security, Spring Data JPA (Hibernate).
- **Frontend**: HTML5, Thymeleaf, Tailwind CSS (via CDN), FontAwesome.
- **Database**: MySQL 8.x.
- **Tools**: Maven, Lombok, Java 17+.

## ⚙️ Prerequisites

1. **Java Development Kit (JDK) 17 or higher**.
2. **Apache Maven**.
3. **MySQL Server** running on `localhost:3306`.
4. Create a database named `parknova`.

## 📂 Project Structure

```text
parknova/
├── src/main/java/com/parknova/
│   ├── controller/      # Web controllers for routing
│   ├── model/           # JPA Entities (User, Slot, Booking)
│   ├── repository/      # Spring Data JPA Interfaces
│   ├── service/         # Business Logic Layer
│   ├── security/        # Auth & Security Configuration
│   └── ParknovaApplication.java
├── src/main/resources/
│   ├── templates/       # Thymeleaf HTML views
│   └── application.properties
└── pom.xml              # Maven dependencies
```

## 🏁 Step-by-Step Run Instructions

1. **Database Setup**:
   - Open your MySQL terminal or Workbench.
   - Run: `CREATE DATABASE parknova;`
   - Update `src/main/resources/application.properties` with your MySQL username and password (default is `root`/`root`).

2. **Build and Run**:
   - Open a terminal in the project root directory (`parknova/`).
   - Run the following command:
     ```bash
     mvn spring-boot:run
     ```

3. **Access the Application**:
   - Navigate to `http://localhost:8080` in your browser.
   - **Default Admin Credentials**:
     - Username: `admin` | Password: `admin`
   - **Default User Credentials**:
     - Username: `user` | Password: `user` (or register a new account).

## 📊 Sample Data
The application automatically seeds initial parking slots and users on the first run using the `DataInitializer` component.

## 🌙 Dark Mode
Toggle between Dark and Light mode using the sun/moon icon in the navbar. Your preference will be saved locally.

---
**Developed by Antigravity (Advanced Agentic Coding)**
