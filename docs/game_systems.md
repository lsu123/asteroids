# Game Systems Module Documentation

## Overview

The **game_systems** module provides the procedural generation and spawning systems for an Asteroids-style game. It implements a timer-based asteroid spawning mechanism that continuously generates asteroids from the edges of the screen, creating dynamic gameplay challenges. The module's primary component, `AsteroidField`, manages the lifecycle of asteroid creation with randomized properties to ensure varied and engaging gameplay.

## Purpose

This module serves as the game's content generation layer, providing:
- **Procedural asteroid spawning**: Automated generation of asteroids at configurable intervals
- **Edge-based spawning**: Asteroids spawn from screen edges and travel inward
- **Randomized properties**: Variable size, speed, direction, and spawn location for each asteroid
- **Difficulty scaling**: Configurable spawn rates and asteroid characteristics
- **Separation of concerns**: Decouples entity creation from entity behavior (see [game_entities](game_entities.md))

## Architecture Overview

The game_systems module implements a spawner pattern that operates independently of individual entity logic. It uses a timer-based system to periodically create new asteroids with randomized attributes, ensuring a continuous stream of challenges for the player.

```mermaid
graph TB
    subgraph "game_systems Module"
        AF[AsteroidField<br/>Spawner System]
        EDGES[Edge Definitions<br/>4 Screen Edges]
        TIMER[Spawn Timer<br/>Interval Tracking]
    end
    
    subgraph "game_entities Module"
        AST[Asteroid<br/>Entity]
    end
    
    subgraph "External Dependencies"
        PG[pygame.sprite.Sprite]
        CONST[constants<br/>Configuration]
        RAND[random<br/>Randomization]
    end
    
    subgraph "Game Loop"
        MAIN[Main Game Loop]
        UPDATE[Update Cycle]
    end
    
    PG --> AF
    CONST --> AF
    RAND --> AF
    AF --> AST
    EDGES --> AF
    TIMER --> AF
    MAIN --> UPDATE
    UPDATE --> AF
    AF -.creates.-> AST
    
    style AF fill:#e1f5ff,stroke:#0066cc,stroke-width:3px
    style AST fill:#ffe1e1,stroke:#cc0000
    style EDGES fill:#fff4e1,stroke:#cc8800
    style TIMER fill:#fff4e1,stroke:#cc8800
```

### System Architecture

```mermaid
classDiagram
    pygame_sprite_Sprite <|-- AsteroidField
    AsteroidField ..> Asteroid : creates
    
    class pygame_sprite_Sprite {
        <<external>>
        +containers
        +kill()
    }
    
    class AsteroidField {
        +list~tuple~ edges
        +float spawn_timer
        +__init__()
        +spawn(radius, position, velocity)
        +update(dt)
    }
    
    class Asteroid {
        <<from game_entities>>
        +Vector2 position
        +Vector2 velocity
        +float radius
        +__init__(x, y, radius)
    }
    
    note for AsteroidField "Manages procedural generation\nof asteroids from screen edges"
```

## Core Components

### AsteroidField (Spawner System)

**Purpose**: Manages the procedural generation of asteroids by spawning them at regular intervals from randomized screen edge positions with varied properties.

**Key Responsibilities**:
- Track spawn timing using an accumulating timer
- Select random spawn edges (top, bottom, left, right)
- Generate randomized asteroid properties (size, speed, direction)
- Create asteroid entities at calculated positions and velocities
- Integrate with Pygame's sprite container system

**Attributes**:
- `edges` (class variable): List of 4 edge definitions, each containing:
  - Direction vector (pygame.Vector2): Inward-pointing direction from edge
  - Position lambda: Function to calculate spawn position along edge
- `spawn_timer` (float): Accumulated time since last spawn (seconds)

**Methods**:
- `__init__()`: Initialize the spawner and register with sprite containers
- `spawn(radius, position, velocity)`: Create a new asteroid with specified properties
- `update(dt)`: Accumulate time and trigger spawns at configured intervals

**Constants Used**:
- `ASTEROID_SPAWN_RATE_SECONDS`: Time interval between spawns
- `ASTEROID_MAX_RADIUS`: Maximum asteroid size (used for edge offset)
- `ASTEROID_MIN_RADIUS`: Minimum asteroid size (base unit for sizing)
- `ASTEROID_KINDS`: Number of different asteroid size categories
- `SCREEN_WIDTH`: Width of the game screen
- `SCREEN_HEIGHT`: Height of the game screen

## Edge Definition System

The `AsteroidField` uses a sophisticated edge system to spawn asteroids from all four screen boundaries. Each edge is defined by a direction vector and a position calculation function.

### Edge Configuration

```mermaid
graph TD
    subgraph "Screen Edges"
        LEFT[Left Edge<br/>Direction: 1,0<br/>X: -MAX_RADIUS<br/>Y: random * HEIGHT]
        RIGHT[Right Edge<br/>Direction: -1,0<br/>X: WIDTH + MAX_RADIUS<br/>Y: random * HEIGHT]
        TOP[Top Edge<br/>Direction: 0,1<br/>X: random * WIDTH<br/>Y: -MAX_RADIUS]
        BOTTOM[Bottom Edge<br/>Direction: 0,-1<br/>X: random * WIDTH<br/>Y: HEIGHT + MAX_RADIUS]
    end
    
    CENTER[Screen Center]
    
    LEFT -.->|Travels Right| CENTER
    RIGHT -.->|Travels Left| CENTER
    TOP -.->|Travels Down| CENTER
    BOTTOM -.->|Travels Up| CENTER
    
    style LEFT fill:#ffe1e1
    style RIGHT fill:#ffe1e1
    style TOP fill:#ffe1e1
    style BOTTOM fill:#ffe1e1
    style CENTER fill:#e1ffe1
```

### Edge Data Structure

Each edge in the `edges` list is a tuple containing:

1. **Direction Vector** (pygame.Vector2): Base direction toward screen center
   - Left edge: `(1, 0)` - points right
   - Right edge: `(-1, 0)` - points left
   - Top edge: `(0, 1)` - points down
   - Bottom edge: `(0, -1)` - points up

2. **Position Lambda** (function): Calculates spawn position along edge
   - Takes random value `0.0` to `1.0` as parameter
   - Returns pygame.Vector2 with calculated position
   - Positions are offset by `ASTEROID_MAX_RADIUS` to spawn off-screen

```python
# Edge structure example
edges = [
    # Left edge
    [
        pygame.Vector2(1, 0),  # Direction: right
        lambda y: pygame.Vector2(-ASTEROID_MAX_RADIUS, y * SCREEN_HEIGHT)
    ],
    # Right edge
    [
        pygame.Vector2(-1, 0),  # Direction: left
        lambda y: pygame.Vector2(SCREEN_WIDTH + ASTEROID_MAX_RADIUS, y * SCREEN_HEIGHT)
    ],
    # Top edge
    [
        pygame.Vector2(0, 1),  # Direction: down
        lambda x: pygame.Vector2(x * SCREEN_WIDTH, -ASTEROID_MAX_RADIUS)
    ],
    # Bottom edge
    [
        pygame.Vector2(0, -1),  # Direction: up
        lambda x: pygame.Vector2(x * SCREEN_WIDTH, SCREEN_HEIGHT + ASTEROID_MAX_RADIUS)
    ]
]
```

## Spawn Process

### Timer-Based Spawning

The `AsteroidField` uses an accumulating timer to trigger spawns at regular intervals:

```mermaid
stateDiagram-v2
    [*] --> Accumulating
    Accumulating --> CheckTimer: update(dt) called
    CheckTimer --> Accumulating: timer < SPAWN_RATE
    CheckTimer --> Spawning: timer >= SPAWN_RATE
    Spawning --> ResetTimer: Asteroid created
    ResetTimer --> Accumulating: timer = 0
    
    note right of Accumulating
        spawn_timer += dt
    end note
    
    note right of Spawning
        1. Select random edge
        2. Calculate properties
        3. Create asteroid
    end note
```

### Randomization Algorithm

When spawning an asteroid, the system randomizes multiple properties:

```mermaid
flowchart TD
    A[Spawn Triggered] --> B[Select Random Edge<br/>1 of 4 edges]
    B --> C[Generate Base Speed<br/>random 40-100 px/s]
    C --> D[Calculate Base Velocity<br/>edge_direction * speed]
    D --> E[Apply Random Rotation<br/>±30 degrees]
    E --> F[Calculate Spawn Position<br/>edge_lambda random 0-1]
    F --> G[Select Asteroid Kind<br/>random 1 to ASTEROID_KINDS]
    G --> H[Calculate Radius<br/>ASTEROID_MIN_RADIUS * kind]
    H --> I[Create Asteroid<br/>spawn radius, position, velocity]
    
    style A fill:#e1f5ff
    style I fill:#ccffcc
```

### Detailed Spawn Flow

```mermaid
sequenceDiagram
    participant GameLoop
    participant AsteroidField
    participant Random
    participant Asteroid
    participant SpriteGroups
    
    GameLoop->>AsteroidField: update(dt)
    AsteroidField->>AsteroidField: spawn_timer += dt
    
    alt spawn_timer > ASTEROID_SPAWN_RATE_SECONDS
        AsteroidField->>AsteroidField: spawn_timer = 0
        AsteroidField->>Random: choice(edges)
        Random-->>AsteroidField: selected_edge
        
        AsteroidField->>Random: randint(40, 100)
        Random-->>AsteroidField: speed
        
        AsteroidField->>AsteroidField: velocity = edge[0] * speed
        AsteroidField->>Random: randint(-30, 30)
        Random-->>AsteroidField: rotation_angle
        AsteroidField->>AsteroidField: velocity.rotate(rotation_angle)
        
        AsteroidField->>Random: uniform(0, 1)
        Random-->>AsteroidField: edge_position
        AsteroidField->>AsteroidField: position = edge[1](edge_position)
        
        AsteroidField->>Random: randint(1, ASTEROID_KINDS)
        Random-->>AsteroidField: kind
        AsteroidField->>AsteroidField: radius = ASTEROID_MIN_RADIUS * kind
        
        AsteroidField->>AsteroidField: spawn(radius, position, velocity)
        AsteroidField->>Asteroid: __init__(position.x, position.y, radius)
        Asteroid->>SpriteGroups: Register in containers
        Asteroid-->>AsteroidField: Asteroid created
        AsteroidField->>Asteroid: Set velocity
    end
```

## Data Flow

### Update Cycle

```mermaid
flowchart LR
    subgraph "Game Loop"
        A[Frame Start] --> B[Calculate dt<br/>Delta Time]
    end
    
    subgraph "AsteroidField Update"
        B --> C[update dt called]
        C --> D[spawn_timer += dt]
        D --> E{timer > SPAWN_RATE?}
        E -->|No| F[Continue]
        E -->|Yes| G[Reset timer to 0]
        G --> H[Randomize Properties]
        H --> I[spawn called]
    end
    
    subgraph "Asteroid Creation"
        I --> J[Create Asteroid Instance]
        J --> K[Set Position]
        K --> L[Set Velocity]
        L --> M[Register in Sprite Groups]
    end
    
    M --> N[Frame End]
    F --> N
    
    style A fill:#e1f5ff
    style C fill:#ffe1e1
    style J fill:#ccffcc
```

### Property Calculation Flow

```mermaid
flowchart TD
    subgraph "Edge Selection"
        A[Random Edge] --> B{Which Edge?}
        B -->|Left| C1[Direction: 1,0<br/>X: -MAX_R, Y: rand*H]
        B -->|Right| C2[Direction: -1,0<br/>X: W+MAX_R, Y: rand*H]
        B -->|Top| C3[Direction: 0,1<br/>X: rand*W, Y: -MAX_R]
        B -->|Bottom| C4[Direction: 0,-1<br/>X: rand*W, Y: H+MAX_R]
    end
    
    subgraph "Velocity Calculation"
        C1 & C2 & C3 & C4 --> D[Base Speed<br/>40-100 px/s]
        D --> E[velocity = direction * speed]
        E --> F[Rotate ±30°]
    end
    
    subgraph "Size Calculation"
        G[Random Kind<br/>1 to ASTEROID_KINDS] --> H[radius = MIN_R * kind]
    end
    
    F --> I[Final Velocity]
    H --> J[Final Radius]
    C1 & C2 & C3 & C4 --> K[Final Position]
    
    I & J & K --> L[Create Asteroid]
    
    style A fill:#e1f5ff
    style L fill:#ccffcc
```

## Component Interactions

### AsteroidField-Asteroid Interaction

```mermaid
sequenceDiagram
    participant AF as AsteroidField
    participant A as Asteroid
    participant SG as Sprite Groups
    
    Note over AF: Timer expires
    AF->>AF: Calculate spawn properties
    AF->>AF: spawn(radius, position, velocity)
    AF->>A: new Asteroid(x, y, radius)
    A->>SG: Register in containers
    A-->>AF: Asteroid instance
    AF->>A: asteroid.velocity = calculated_velocity
    
    Note over A: Asteroid now autonomous
    Note over A: Managed by game loop
```

### Integration with Game Loop

```mermaid
flowchart TD
    subgraph "Main Game Loop"
        A[Game Start] --> B[Initialize AsteroidField]
        B --> C[Game Loop Iteration]
        C --> D[Calculate dt]
    end
    
    subgraph "Sprite Group Updates"
        D --> E[Update All Sprites]
        E --> F[AsteroidField.update dt]
        E --> G[Asteroid.update dt]
        E --> H[Player.update dt]
        E --> I[Shot.update dt]
    end
    
    subgraph "AsteroidField Processing"
        F --> J{Spawn Timer?}
        J -->|Ready| K[Create New Asteroid]
        J -->|Not Ready| L[Continue]
        K --> M[Add to Sprite Groups]
    end
    
    M --> N[Render Frame]
    L --> N
    G --> N
    H --> N
    I --> N
    N --> C
    
    style B fill:#e1f5ff
    style F fill:#ffe1e1
    style K fill:#ccffcc
```

## Asteroid Lifecycle

### From Spawn to Destruction

```mermaid
stateDiagram-v2
    [*] --> Spawning: Timer triggers
    Spawning --> OffScreen: Created at edge
    OffScreen --> OnScreen: Travels inward
    OnScreen --> Hit: Player shoots
    OnScreen --> OffScreen: Travels past screen
    Hit --> Split: Asteroid.split()
    Split --> [*]: Original destroyed
    Split --> Spawning: Children created
    OffScreen --> [*]: Cleanup (if implemented)
    
    note right of Spawning
        AsteroidField.spawn()
        creates new Asteroid
    end note
    
    note right of Split
        See game_entities module
        for split mechanics
    end note
```

### Spawn-to-Split Integration

The `AsteroidField` is involved in both initial spawning and child asteroid creation during splits:

```mermaid
flowchart TD
    subgraph "Initial Spawn"
        A[AsteroidField Timer] --> B[spawn called]
        B --> C[Create Parent Asteroid]
    end
    
    subgraph "Gameplay"
        C --> D[Asteroid Travels]
        D --> E{Hit by Shot?}
        E -->|No| D
        E -->|Yes| F[Asteroid.split]
    end
    
    subgraph "Split Process"
        F --> G[Original Destroyed]
        G --> H{Size Check}
        H -->|Too Small| I[End]
        H -->|Large Enough| J[Create 2 Children]
        J --> K[Child 1: AsteroidField.spawn]
        J --> L[Child 2: AsteroidField.spawn]
    end
    
    K --> M[New Asteroid 1]
    L --> N[New Asteroid 2]
    M --> D
    N --> D
    
    style A fill:#e1f5ff
    style C fill:#ccffcc
    style F fill:#ffcccc
    style M fill:#ccffcc
    style N fill:#ccffcc
```

## Configuration and Tuning

### Spawn Rate Configuration

The spawn rate directly affects game difficulty:

```mermaid
graph LR
    subgraph "Difficulty Levels"
        EASY[Easy Mode<br/>SPAWN_RATE = 2.0s]
        MEDIUM[Medium Mode<br/>SPAWN_RATE = 1.2s]
        HARD[Hard Mode<br/>SPAWN_RATE = 0.8s]
    end
    
    subgraph "Asteroid Density"
        LOW[Low Density<br/>Few asteroids]
        MED[Medium Density<br/>Moderate challenge]
        HIGH[High Density<br/>Intense gameplay]
    end
    
    EASY --> LOW
    MEDIUM --> MED
    HARD --> HIGH
    
    style EASY fill:#ccffcc
    style MEDIUM fill:#ffffcc
    style HARD fill:#ffcccc
```

### Randomization Parameters

| Parameter | Range | Purpose |
|-----------|-------|---------|
| **Edge Selection** | 1 of 4 edges | Determines spawn location |
| **Base Speed** | 40-100 px/s | Controls asteroid velocity |
| **Direction Variance** | ±30 degrees | Adds unpredictability to trajectory |
| **Edge Position** | 0.0-1.0 | Random position along selected edge |
| **Asteroid Kind** | 1 to ASTEROID_KINDS | Determines size category |

### Size Categories

Asteroids are spawned in discrete size categories:

```mermaid
graph TD
    subgraph "Asteroid Sizes"
        K1[Kind 1<br/>radius = MIN_R * 1<br/>Smallest]
        K2[Kind 2<br/>radius = MIN_R * 2<br/>Medium]
        K3[Kind 3<br/>radius = MIN_R * 3<br/>Large]
        KN[Kind N<br/>radius = MIN_R * N<br/>Largest]
    end
    
    SPAWN[Random Kind Selection] --> K1
    SPAWN --> K2
    SPAWN --> K3
    SPAWN --> KN
    
    K1 -.->|Split once| NONE[No children]
    K2 -.->|Split once| K1
    K3 -.->|Split once| K2
    KN -.->|Split once| K3
    
    style SPAWN fill:#e1f5ff
    style K1 fill:#ccffcc
    style K2 fill:#ffffcc
    style K3 fill:#ffccaa
    style KN fill:#ffcccc
```

## Integration with Game Entities

The game_systems module works closely with the game_entities module (see [game_entities](game_entities.md)):

### Dependency Relationship

```mermaid
graph LR
    subgraph "game_systems"
        AF[AsteroidField]
    end
    
    subgraph "game_entities"
        AST[Asteroid]
        CS[CircleShape]
    end
    
    AF -->|creates| AST
    AST -->|calls spawn on| AF
    CS -->|base class| AST
    
    style AF fill:#e1f5ff
    style AST fill:#ffe1e1
```

### Circular Dependency Handling

The `Asteroid.split()` method imports `AsteroidField` locally to avoid circular import issues:

```python
# In Asteroid.split()
from asteroidfield import AsteroidField  # Local import
AsteroidField().spawn(new_radius, self.position, new_velocity)
```

This design allows:
- `AsteroidField` to create initial `Asteroid` instances
- `Asteroid` to use `AsteroidField.spawn()` for creating children during splits
- Avoidance of circular import errors

## Design Patterns

### 1. Spawner Pattern

`AsteroidField` implements the Spawner pattern:
- Centralized creation logic for game entities
- Decouples entity creation from entity behavior
- Manages spawn timing and frequency
- Provides consistent initialization

### 2. Factory Method Pattern

The `spawn()` method acts as a factory:
- Encapsulates object creation logic
- Provides a consistent interface for creating asteroids
- Used by both timer-based spawning and split-based spawning

### 3. Strategy Pattern (Implicit)

Edge definitions use strategy pattern:
- Each edge has its own position calculation strategy (lambda function)
- Direction vectors define movement strategy
- Allows easy addition of new spawn patterns

### 4. Timer Pattern

Spawn timing uses accumulator pattern:
- Accumulates delta time across frames
- Triggers action when threshold reached
- Resets timer for next cycle

## Performance Considerations

### Sprite Container Integration

The `AsteroidField` inherits from `pygame.sprite.Sprite` and registers with containers:

```python
def __init__(self):
    pygame.sprite.Sprite.__init__(self, self.containers)
    self.spawn_timer = 0.0
```

**Benefits**:
- Automatic inclusion in sprite group updates
- Centralized update management via game loop
- No manual tracking required

**Considerations**:
- `AsteroidField` itself doesn't need rendering (no `draw()` method)
- Exists primarily for update cycle integration
- Could alternatively be managed outside sprite system

### Spawn Rate Impact

Spawn rate affects performance and gameplay:

```mermaid
graph TD
    A[Low Spawn Rate] --> B[Fewer Asteroids]
    B --> C[Better Performance]
    B --> D[Easier Gameplay]
    
    E[High Spawn Rate] --> F[More Asteroids]
    F --> G[Higher CPU/Memory Usage]
    F --> H[Harder Gameplay]
    
    style A fill:#ccffcc
    style E fill:#ffcccc
```

**Optimization Strategies**:
- Limit maximum active asteroids
- Implement off-screen culling
- Use object pooling for asteroid instances
- Adjust spawn rate based on performance metrics

## Usage Example

### Basic Setup

```python
import pygame
from asteroidfield import AsteroidField
from asteroid import Asteroid

# Initialize sprite groups
updatable = pygame.sprite.Group()
drawable = pygame.sprite.Group()
asteroids = pygame.sprite.Group()

# Set containers for automatic registration
AsteroidField.containers = (updatable,)
Asteroid.containers = (updatable, drawable, asteroids)

# Create asteroid field
asteroid_field = AsteroidField()

# Game loop
dt = 0
clock = pygame.time.Clock()

while running:
    dt = clock.tick(60) / 1000  # Delta time in seconds
    
    # Update all sprites (including AsteroidField)
    for sprite in updatable:
        sprite.update(dt)
    
    # AsteroidField automatically spawns asteroids
    # New asteroids are automatically added to groups
```

### Custom Spawn Configuration

```python
# Modify spawn rate
from constants import ASTEROID_SPAWN_RATE_SECONDS

# Faster spawning for hard mode
ASTEROID_SPAWN_RATE_SECONDS = 0.8

# Slower spawning for easy mode
ASTEROID_SPAWN_RATE_SECONDS = 2.0
```

### Manual Spawning

```python
# Manually spawn an asteroid
import pygame
from asteroidfield import AsteroidField

field = AsteroidField()

# Spawn a large asteroid at center moving right
position = pygame.Vector2(400, 300)
velocity = pygame.Vector2(50, 0)
radius = 60

field.spawn(radius, position, velocity)
```

## Extension Points

### Adding New Spawn Patterns

The edge system can be extended with new spawn patterns:

```python
# Add diagonal spawns
AsteroidField.edges.extend([
    # Top-left corner
    [
        pygame.Vector2(1, 1).normalize(),
        lambda _: pygame.Vector2(-ASTEROID_MAX_RADIUS, -ASTEROID_MAX_RADIUS)
    ],
    # Top-right corner
    [
        pygame.Vector2(-1, 1).normalize(),
        lambda _: pygame.Vector2(SCREEN_WIDTH + ASTEROID_MAX_RADIUS, -ASTEROID_MAX_RADIUS)
    ]
])
```

### Dynamic Difficulty Scaling

Implement progressive difficulty:

```python
class AsteroidField(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(self.containers)
        self.spawn_timer = 0.0
        self.game_time = 0.0
        self.base_spawn_rate = ASTEROID_SPAWN_RATE_SECONDS
    
    def update(self, dt):
        self.game_time += dt
        self.spawn_timer += dt
        
        # Decrease spawn rate over time (faster spawning)
        current_spawn_rate = max(0.5, self.base_spawn_rate - (self.game_time / 60))
        
        if self.spawn_timer > current_spawn_rate:
            # Spawn logic...
            pass
```

### Spawn Zones

Create specific spawn zones for different asteroid types:

```python
class AsteroidField(pygame.sprite.Sprite):
    def spawn_in_zone(self, zone_name):
        zones = {
            'left': self.edges[0],
            'right': self.edges[1],
            'top': self.edges[2],
            'bottom': self.edges[3]
        }
        edge = zones[zone_name]
        # Spawn logic using specific edge...
```

## Testing Considerations

### Unit Testing

Key test cases for `AsteroidField`:

```python
def test_spawn_creates_asteroid():
    """Verify spawn creates asteroid with correct properties"""
    field = AsteroidField()
    position = pygame.Vector2(100, 100)
    velocity = pygame.Vector2(50, 0)
    radius = 40
    
    field.spawn(radius, position, velocity)
    # Assert asteroid created with correct properties

def test_timer_triggers_spawn():
    """Verify timer triggers spawn at correct interval"""
    field = AsteroidField()
    dt = ASTEROID_SPAWN_RATE_SECONDS + 0.1
    
    field.update(dt)
    # Assert spawn was triggered

def test_randomization():
    """Verify spawn properties are randomized"""
    field = AsteroidField()
    spawns = []
    
    for _ in range(100):
        field.update(ASTEROID_SPAWN_RATE_SECONDS + 0.1)
        # Collect spawn properties
    
    # Assert variety in edge selection, speed, rotation, etc.
```

### Integration Testing

```python
def test_asteroid_field_integration():
    """Verify AsteroidField integrates with sprite groups"""
    updatable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    
    AsteroidField.containers = (updatable,)
    Asteroid.containers = (updatable, asteroids)
    
    field = AsteroidField()
    
    # Simulate multiple updates
    for _ in range(10):
        field.update(ASTEROID_SPAWN_RATE_SECONDS + 0.1)
    
    # Assert asteroids were created and added to groups
    assert len(asteroids) > 0
```

## Summary

The **game_systems** module provides essential procedural generation capabilities for the Asteroids game:

**Key Features**:
- ✅ Timer-based automatic spawning
- ✅ Randomized asteroid properties (size, speed, direction, position)
- ✅ Edge-based spawn system for natural gameplay flow
- ✅ Integration with sprite container system
- ✅ Support for both initial spawning and split-based spawning

**Design Strengths**:
- Clear separation between spawning logic and entity behavior
- Highly configurable through constants
- Extensible edge and spawn pattern system
- Efficient timer-based triggering

**Integration Points**:
- Creates `Asteroid` entities from [game_entities](game_entities.md)
- Used by `Asteroid.split()` for child creation
- Managed by main game loop through sprite groups
- Configured via centralized constants module

The module exemplifies good game architecture by separating content generation from entity logic, enabling independent testing, modification, and extension of both systems.
