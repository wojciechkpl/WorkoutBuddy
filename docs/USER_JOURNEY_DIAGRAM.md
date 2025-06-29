# WorkoutBuddy User Journey Diagram (2024)

## Overview

This document illustrates the complete user journey through the WorkoutBuddy application, including new flows for safety, privacy, ML feedback, accountability, and community. All flows are covered by synthetic test data and integration tests.

## Complete User Journey

```mermaid
journey
    title WorkoutBuddy User Journey
    section Onboarding
      User discovers app: 5: User
      Download/Install app: 5: User
      Create account: 5: User
      Set unit preferences: 4: User
      Complete fitness profile: 4: User
      Set fitness goals: 4: User
    section Daily Usage
      Open app: 5: User
      View dashboard: 5: User
      Check progress: 4: User
      Plan workout: 4: User
      Get exercise recommendations: 4: User
      Start workout: 5: User
      Log exercises: 4: User
      Complete workout: 5: User
      View results: 4: User
    section Social Features
      Connect with friends: 3: User
      Share achievements: 3: User
      Join challenges: 3: User
      Compare progress: 3: User
    section Safety & Privacy
      Block/report user: 3: User
      Adjust privacy settings: 3: User
      Verify account: 2: User
    section Accountability & Community
      Join community group: 3: User
      Log accountability check-in: 3: User
      Give feedback on ML: 2: User
    section Advanced Features
      Analyze performance: 3: User
      Adjust goals: 3: User
      Get personalized insights: 4: User
      Update preferences: 2: User
```

## Test Coverage Note

All flows above are covered by synthetic test data and integration tests. Test data is annotated for easy separation and cleanup.

## Detailed User Journey Flow

```mermaid
flowchart TD
    %% Initial Discovery & Onboarding
    Start([User Discovers WorkoutBuddy]) --> Download[Download Mobile App]
    Download --> Install[Install & Launch App]
    Install --> Welcome[Welcome Screen]

    Welcome --> Onboarding{First Time User?}
    Onboarding -->|Yes| CreateAccount[Create Account]
    Onboarding -->|No| Login[Login to Account]

    CreateAccount --> UnitSetup[Set Unit Preferences]
    Login --> UnitSetup

    %% Unit Preference Setup
    UnitSetup --> UnitChoice{Choose Unit System}
    UnitChoice -->|Metric| MetricSetup[Set Metric Units<br/>Height: CM<br/>Weight: KG<br/>Distance: KM]
    UnitChoice -->|Imperial| ImperialSetup[Set Imperial Units<br/>Height: Inches/Feet<br/>Weight: LBS<br/>Distance: Miles]

    MetricSetup --> ProfileSetup[Complete Fitness Profile]
    ImperialSetup --> ProfileSetup

    %% Profile Setup
    ProfileSetup --> HeightInput[Enter Height<br/>In preferred units]
    HeightInput --> WeightInput[Enter Weight<br/>In preferred units]
    WeightInput --> AgeInput[Enter Age]
    AgeInput --> GoalSelection[Select Fitness Goal]

    GoalSelection --> ExperienceLevel[Select Experience Level]
    ExperienceLevel --> ProfileComplete[Profile Complete]

    %% Main App Flow
    ProfileComplete --> Dashboard[Dashboard View<br/>Progress Overview]
    Dashboard --> MainMenu{User Action}

    %% Workout Planning Flow
    MainMenu -->|Plan Workout| WorkoutPlanning[Workout Planning]
    WorkoutPlanning --> GetRecommendations[Get AI Recommendations<br/>Based on profile & history]
    GetRecommendations --> ExerciseSelection[Select Exercises<br/>With unit-specific weights]
    ExerciseSelection --> WorkoutScheduled[Workout Scheduled]

    %% Workout Execution Flow
    MainMenu -->|Start Workout| WorkoutStart[Start Workout]
    WorkoutStart --> ExerciseExecution[Execute Exercises<br/>Log sets, reps, weights]
    ExerciseExecution --> UnitLogging[Log in preferred units<br/>Auto-convert for ML]
    UnitLogging --> WorkoutComplete[Workout Complete]

    %% Progress Tracking Flow
    MainMenu -->|View Progress| ProgressView[Progress Dashboard]
    ProgressView --> StatsDisplay[Display Statistics<br/>In preferred units]
    StatsDisplay --> ProgressAnalysis[AI Analysis<br/>Metric-based insights]

    %% Social Features Flow
    MainMenu -->|Social| SocialFeatures[Social Features]
    SocialFeatures --> FindFriends[Find Friends<br/>Similar fitness goals]
    FindFriends --> ShareProgress[Share Progress<br/>Unit-appropriate display]

    %% Settings & Preferences
    MainMenu -->|Settings| SettingsMenu[Settings Menu]
    SettingsMenu --> UnitPreferences[Unit Preferences]
    UnitPreferences --> ChangeUnits{Change Units?}
    ChangeUnits -->|Yes| UnitConversion[Convert existing data<br/>Update display]
    ChangeUnits -->|No| SettingsComplete[Settings Updated]
    UnitConversion --> SettingsComplete

    %% Return to Main Flow
    WorkoutScheduled --> Dashboard
    WorkoutComplete --> Dashboard
    ProgressAnalysis --> Dashboard
    ShareProgress --> Dashboard
    SettingsComplete --> Dashboard

    %% Styling
    classDef onboarding fill:#e1f5fe
    classDef unitSystem fill:#f3e5f5
    classDef workout fill:#e8f5e8
    classDef social fill:#fff3e0
    classDef settings fill:#fce4ec

    class Start,Download,Install,Welcome,CreateAccount,Login onboarding
    class UnitSetup,UnitChoice,MetricSetup,ImperialSetup unitSystem
    class WorkoutPlanning,GetRecommendations,ExerciseSelection,WorkoutStart,ExerciseExecution,UnitLogging,WorkoutComplete workout
    class SocialFeatures,FindFriends,ShareProgress social
    class SettingsMenu,UnitPreferences,ChangeUnits,UnitConversion settings
```

## Unit System Integration Journey

```mermaid
sequenceDiagram
    participant U as User
    participant UI as Mobile App
    participant API as Backend API
    participant DB as Database
    participant ML as ML Service
    participant UC as Unit Converter

    Note over U,UC: User Onboarding with Unit Preferences

    U->>UI: Open app for first time
    UI->>U: Show unit preference selection
    U->>UI: Select Imperial units (LBS, Inches)
    UI->>API: Send unit preferences
    API->>DB: Store user preferences
    DB-->>API: Confirm storage
    API-->>UI: Preferences saved
    UI-->>U: Show profile setup

    U->>UI: Enter height: 70 inches
    U->>UI: Enter weight: 150 lbs
    UI->>API: Send profile data
    API->>UC: Convert to metric for ML
    UC->>API: Height: 177.8 cm, Weight: 68.04 kg
    API->>DB: Store in user's units + metric for ML
    DB-->>API: Data stored
    API-->>UI: Profile complete
    UI-->>U: Show dashboard

    Note over U,UC: Daily Workout with Unit Conversion

    U->>UI: Start workout
    UI->>API: Get exercise recommendations
    API->>ML: Request recommendations (metric data)
    ML->>DB: Query metric views
    DB-->>ML: Return metric data
    ML-->>API: Exercise recommendations
    API->>UC: Convert recommendations to user units
    UC-->>API: Recommendations in LBS/Inches
    API-->>UI: Show recommendations
    UI-->>U: Display exercises with imperial units

    U->>UI: Log exercise: Bench Press 135 lbs
    UI->>API: Send workout data
    API->>UC: Convert to metric for storage
    UC->>API: 61.24 kg
    API->>DB: Store in metric + user units
    DB-->>API: Data stored
    API-->>UI: Exercise logged
    UI-->>U: Show progress in imperial units

    Note over U,UC: Progress Analysis with Unit Flexibility

    U->>UI: View progress dashboard
    UI->>API: Request progress data
    API->>DB: Get user's data
    DB-->>API: Return in user's units
    API->>ML: Request analysis (metric)
    ML->>DB: Query metric views
    DB-->>ML: Return metric data
    ML-->>API: Analysis results (metric)
    API->>UC: Convert insights to user units
    UC-->>API: Insights in imperial
    API-->>UI: Progress + insights
    UI-->>U: Display in preferred units
```

## User Experience with Unit System

```mermaid
graph LR
    %% User Interface States
    subgraph "User Interface States"
        Onboarding[Onboarding<br/>Unit Selection]
        Profile[Profile Setup<br/>Unit-specific Input]
        Dashboard[Dashboard<br/>Unit-appropriate Display]
        Workout[Workout<br/>Unit-aware Logging]
        Progress[Progress<br/>Unit-converted Stats]
        Settings[Settings<br/>Unit Management]
    end

    %% Unit System Integration
    subgraph "Unit System Integration"
        UnitSelection[Unit Selection<br/>METRIC/IMPERIAL]
        InputValidation[Input Validation<br/>Unit-specific Ranges]
        DisplayConversion[Display Conversion<br/>User Preferences]
        StorageConversion[Storage Conversion<br/>Metric for ML]
        AnalysisConversion[Analysis Conversion<br/>Metric Processing]
    end

    %% Data Flow
    subgraph "Data Flow"
        UserInput[User Input<br/>Preferred Units]
        MetricProcessing[Metric Processing<br/>Algorithms]
        UserOutput[User Output<br/>Preferred Units]
    end

    %% Connections
    Onboarding --> UnitSelection
    Profile --> InputValidation
    Dashboard --> DisplayConversion
    Workout --> StorageConversion
    Progress --> AnalysisConversion
    Settings --> UnitSelection

    UnitSelection --> UserInput
    InputValidation --> UserInput
    DisplayConversion --> UserOutput
    StorageConversion --> MetricProcessing
    AnalysisConversion --> MetricProcessing

    UserInput --> MetricProcessing
    MetricProcessing --> UserOutput
```

## Key User Journey Touchpoints

### 1. **Onboarding Experience**
```mermaid
flowchart TD
    A[App Launch] --> B{First Time?}
    B -->|Yes| C[Welcome Screen]
    B -->|No| D[Login Screen]

    C --> E[Unit Preference Selection]
    E --> F[Choose Unit System]
    F --> G{Metric or Imperial?}

    G -->|Metric| H[Set Metric Units<br/>CM, KG, KM]
    G -->|Imperial| I[Set Imperial Units<br/>Inches, LBS, Miles]

    H --> J[Profile Setup]
    I --> J

    J --> K[Enter Height<br/>In chosen units]
    K --> L[Enter Weight<br/>In chosen units]
    L --> M[Set Fitness Goals]
    M --> N[Dashboard Ready]

    D --> N

    style E fill:#e1f5fe
    style F fill:#e1f5fe
    style G fill:#e1f5fe
    style H fill:#e1f5fe
    style I fill:#e1f5fe
```

### 2. **Workout Planning Journey**
```mermaid
flowchart TD
    A[Plan Workout] --> B[Get AI Recommendations]
    B --> C[ML Service Processes<br/>Metric Data]
    C --> D[Recommendations Generated<br/>Based on User Profile]
    D --> E[Convert to User Units]
    E --> F[Display Exercises<br/>With User's Units]

    F --> G[User Selects Exercises]
    G --> H[Set Target Weights<br/>In User's Units]
    H --> I[Schedule Workout]

    style B fill:#e8f5e8
    style C fill:#e8f5e8
    style D fill:#e8f5e8
    style E fill:#e8f5e8
```

### 3. **Workout Execution Journey**
```mermaid
flowchart TD
    A[Start Workout] --> B[View Exercise List<br/>In User's Units]
    B --> C[Begin Exercise]
    C --> D[Log Sets & Reps]
    D --> E[Log Weight Used<br/>In User's Units]
    E --> F[Auto-convert to Metric<br/>For ML Processing]
    F --> G[Store in Database<br/>Both Units]
    G --> H[Next Exercise]

    H --> I{More Exercises?}
    I -->|Yes| C
    I -->|No| J[Complete Workout]
    J --> K[Show Summary<br/>In User's Units]
    K --> L[Update Progress<br/>Metric-based Analysis]

    style E fill:#e8f5e8
    style F fill:#e8f5e8
    style G fill:#e8f5e8
    style L fill:#e8f5e8
```

### 4. **Progress Tracking Journey**
```mermaid
flowchart TD
    A[View Progress] --> B[Load User Data<br/>In User's Units]
    B --> C[Query Metric Views<br/>For Analysis]
    C --> D[ML Analysis<br/>Metric-based Insights]
    D --> E[Convert Insights<br/>To User's Units]
    E --> F[Display Progress<br/>In Preferred Units]

    F --> G[Show Trends<br/>Weight, Strength, etc.]
    G --> H[AI Recommendations<br/>Based on Progress]
    H --> I[Suggest Goal Adjustments<br/>In User's Units]

    style C fill:#fff3e0
    style D fill:#fff3e0
    style E fill:#fff3e0
    style H fill:#fff3e0
```

### 5. **Settings & Unit Management**
```mermaid
flowchart TD
    A[Access Settings] --> B[View Current Units]
    B --> C{Change Units?}
    C -->|No| D[Other Settings]
    C -->|Yes| E[Select New Units]

    E --> F[Choose New System]
    F --> G{Metric or Imperial?}

    G -->|Metric| H[Set Metric Units]
    G -->|Imperial| I[Set Imperial Units]

    H --> J[Convert Existing Data]
    I --> J

    J --> K[Update Display<br/>All Measurements]
    K --> L[Confirm Changes]
    L --> M[Settings Updated]

    style E fill:#fce4ec
    style F fill:#fce4ec
    style G fill:#fce4ec
    style H fill:#fce4ec
    style I fill:#fce4ec
    style J fill:#fce4ec
```

## User Journey Benefits

### 1. **Seamless Unit Experience**
- Users work in their preferred units throughout the entire journey
- Automatic conversion happens behind the scenes
- No confusion about unit systems

### 2. **Personalized Recommendations**
- ML algorithms use metric data for accuracy
- Recommendations are converted to user's preferred units
- Consistent and reliable suggestions

### 3. **Flexible Data Management**
- Users can change units at any time
- Historical data is preserved and converted
- No data loss when switching units

### 4. **Intuitive Interface**
- Unit selection during onboarding
- Unit-appropriate input validation
- Unit-converted display throughout the app

### 5. **Social Compatibility**
- Users can share progress in their preferred units
- Friends see data in their own units
- No unit confusion in social features

## Key Success Metrics

1. **User Adoption**: % of users who complete unit preference setup
2. **Unit Satisfaction**: User feedback on unit system experience
3. **Data Accuracy**: Reduction in unit-related errors
4. **Feature Usage**: Engagement with ML recommendations
5. **Retention**: User retention after unit preference changes

This user journey ensures that the dual unit system enhances rather than complicates the user experience, providing flexibility while maintaining accuracy and consistency throughout the application.