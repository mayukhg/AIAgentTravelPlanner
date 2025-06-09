# Database Schema

Complete reference for the Multi-Agent Assistant System database schema, including table structures, relationships, and data management patterns.

## Schema Overview

The system uses PostgreSQL as the primary database with SQLAlchemy ORM for data modeling. The schema is designed to support multi-agent conversations, calendar management, and persistent state storage.

### Entity Relationship Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ChatSession   │    │   ChatMessage   │    │   AgentState    │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ id (PK)         │    │ id (PK)         │    │ id (PK)         │
│ session_id      │◄──┐│ session_id (FK) │    │ session_id      │
│ created_at      │   └┤ role            │    │ agent_type      │
└─────────────────┘    │ content         │    │ state_data      │
                       │ agent_type      │    │ updated_at      │
                       │ timestamp       │    └─────────────────┘
                       └─────────────────┘
                                
┌─────────────────┐
│ CalendarEvent   │
├─────────────────┤
│ id (PK)         │
│ title           │
│ description     │
│ start_time      │
│ end_time        │
│ location        │
│ all_day         │
│ created_at      │
│ updated_at      │
└─────────────────┘
```

## Table Specifications

### ChatSession

Stores session metadata for conversation tracking.

```sql
CREATE TABLE chat_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**SQLAlchemy Model**:
```python
class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    
    # Relationships
    messages = db.relationship('ChatMessage', backref='session', lazy=True, 
                              cascade='all, delete-orphan')
```

**Indexes**:
```sql
CREATE INDEX idx_chat_sessions_session_id ON chat_sessions(session_id);
CREATE INDEX idx_chat_sessions_created_at ON chat_sessions(created_at);
```

### ChatMessage

Stores individual messages within conversations with agent attribution.

```sql
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    agent_type VARCHAR(50),
    timestamp TIMESTAMP DEFAULT NOW()
);
```

**SQLAlchemy Model**:
```python
class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), db.ForeignKey('chat_sessions.session_id'), 
                          nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    agent_type = db.Column(db.String(50))  # Which agent handled this message
    timestamp = db.Column(db.DateTime, default=func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'role': self.role,
            'content': self.content,
            'agent_type': self.agent_type,
            'timestamp': self.timestamp.isoformat()
        }
```

**Indexes**:
```sql
CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_timestamp ON chat_messages(timestamp);
CREATE INDEX idx_chat_messages_role ON chat_messages(role);
CREATE INDEX idx_chat_messages_agent_type ON chat_messages(agent_type);
```

### AgentState

Stores persistent state data for individual agents across sessions.

```sql
CREATE TABLE agent_states (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    agent_type VARCHAR(50) NOT NULL,
    state_data TEXT,  -- JSON serialized state
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(session_id, agent_type)
);
```

**SQLAlchemy Model**:
```python
class AgentState(db.Model):
    __tablename__ = 'agent_states'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    agent_type = db.Column(db.String(50), nullable=False)
    state_data = db.Column(db.Text)  # JSON serialized state
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        db.UniqueConstraint('session_id', 'agent_type'),
    )
```

**Indexes**:
```sql
CREATE INDEX idx_agent_states_session_id ON agent_states(session_id);
CREATE INDEX idx_agent_states_agent_type ON agent_states(agent_type);
CREATE INDEX idx_agent_states_updated_at ON agent_states(updated_at);
```

### CalendarEvent

Stores calendar events managed by the Calendar Agent.

```sql
CREATE TABLE calendar_events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    location VARCHAR(200),
    all_day BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**SQLAlchemy Model**:
```python
class CalendarEvent(db.Model):
    __tablename__ = 'calendar_events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    all_day = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'location': self.location,
            'all_day': self.all_day,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def conflicts_with(self, start_time, end_time):
        """Check if this event conflicts with given time range"""
        return not (self.end_time <= start_time or self.start_time >= end_time)
```

**Indexes**:
```sql
CREATE INDEX idx_calendar_events_start_time ON calendar_events(start_time);
CREATE INDEX idx_calendar_events_end_time ON calendar_events(end_time);
CREATE INDEX idx_calendar_events_date_range ON calendar_events(start_time, end_time);
CREATE INDEX idx_calendar_events_title ON calendar_events USING gin(to_tsvector('english', title));
```

## Data Relationships

### Session-Message Relationship

One-to-many relationship between sessions and messages:

```python
# Access messages for a session
session = ChatSession.query.filter_by(session_id='abc123').first()
messages = session.messages.order_by(ChatMessage.timestamp).all()

# Access session from a message
message = ChatMessage.query.first()
session = message.session
```

### Agent State Management

Each agent can maintain state per session:

```python
# Save agent state
def save_agent_state(session_id: str, agent_type: str, state_data: dict):
    agent_state = AgentState.query.filter_by(
        session_id=session_id,
        agent_type=agent_type
    ).first()
    
    if agent_state:
        agent_state.state_data = json.dumps(state_data)
        agent_state.updated_at = func.now()
    else:
        agent_state = AgentState(
            session_id=session_id,
            agent_type=agent_type,
            state_data=json.dumps(state_data)
        )
        db.session.add(agent_state)
    
    db.session.commit()

# Load agent state
def load_agent_state(session_id: str, agent_type: str) -> dict:
    agent_state = AgentState.query.filter_by(
        session_id=session_id,
        agent_type=agent_type
    ).first()
    
    if agent_state and agent_state.state_data:
        return json.loads(agent_state.state_data)
    return {}
```

## Data Access Patterns

### Session Management

```python
class SessionManager:
    @staticmethod
    def create_session(session_id: str) -> ChatSession:
        """Create a new chat session"""
        session = ChatSession(session_id=session_id)
        db.session.add(session)
        db.session.commit()
        return session
    
    @staticmethod
    def get_or_create_session(session_id: str) -> ChatSession:
        """Get existing session or create new one"""
        session = ChatSession.query.filter_by(session_id=session_id).first()
        if not session:
            session = SessionManager.create_session(session_id)
        return session
    
    @staticmethod
    def get_session_history(session_id: str, limit: int = 50) -> List[ChatMessage]:
        """Get message history for a session"""
        return ChatMessage.query.filter_by(session_id=session_id)\
                               .order_by(ChatMessage.timestamp.desc())\
                               .limit(limit).all()
```

### Message Operations

```python
class MessageManager:
    @staticmethod
    def add_message(session_id: str, role: str, content: str, 
                   agent_type: str = None) -> ChatMessage:
        """Add a new message to the session"""
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            agent_type=agent_type
        )
        db.session.add(message)
        db.session.commit()
        return message
    
    @staticmethod
    def get_messages_by_agent(session_id: str, agent_type: str) -> List[ChatMessage]:
        """Get all messages handled by a specific agent in a session"""
        return ChatMessage.query.filter_by(
            session_id=session_id,
            agent_type=agent_type
        ).order_by(ChatMessage.timestamp).all()
```

### Calendar Operations

```python
class CalendarManager:
    @staticmethod
    def create_event(title: str, start_time: datetime, end_time: datetime,
                    description: str = None, location: str = None,
                    all_day: bool = False) -> CalendarEvent:
        """Create a new calendar event"""
        event = CalendarEvent(
            title=title,
            start_time=start_time,
            end_time=end_time,
            description=description,
            location=location,
            all_day=all_day
        )
        db.session.add(event)
        db.session.commit()
        return event
    
    @staticmethod
    def find_conflicts(start_time: datetime, end_time: datetime) -> List[CalendarEvent]:
        """Find events that conflict with the given time range"""
        return CalendarEvent.query.filter(
            CalendarEvent.start_time < end_time,
            CalendarEvent.end_time > start_time
        ).all()
    
    @staticmethod
    def get_events_for_date_range(start_date: datetime, 
                                 end_date: datetime) -> List[CalendarEvent]:
        """Get all events within a date range"""
        return CalendarEvent.query.filter(
            CalendarEvent.start_time >= start_date,
            CalendarEvent.start_time < end_date
        ).order_by(CalendarEvent.start_time).all()
```

## Migration Scripts

### Initial Schema Creation

```python
# migrations/versions/001_initial_schema.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Create chat_sessions table
    op.create_table('chat_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id')
    )
    
    # Create chat_messages table
    op.create_table('chat_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=100), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('agent_type', sa.String(length=50), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['chat_sessions.session_id'], 
                               ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_chat_sessions_session_id', 'chat_sessions', ['session_id'])
    op.create_index('idx_chat_messages_session_id', 'chat_messages', ['session_id'])
    op.create_index('idx_chat_messages_timestamp', 'chat_messages', ['timestamp'])

def downgrade():
    op.drop_index('idx_chat_messages_timestamp', table_name='chat_messages')
    op.drop_index('idx_chat_messages_session_id', table_name='chat_messages')
    op.drop_index('idx_chat_sessions_session_id', table_name='chat_sessions')
    op.drop_table('chat_messages')
    op.drop_table('chat_sessions')
```

## Performance Considerations

### Query Optimization

```python
# Efficient session history retrieval with pagination
def get_paginated_history(session_id: str, page: int = 1, per_page: int = 20):
    return ChatMessage.query.filter_by(session_id=session_id)\
                           .order_by(ChatMessage.timestamp.desc())\
                           .paginate(page=page, per_page=per_page, error_out=False)

# Bulk insert for performance
def bulk_insert_messages(messages_data: List[dict]):
    messages = [ChatMessage(**data) for data in messages_data]
    db.session.bulk_save_objects(messages)
    db.session.commit()
```

### Index Usage

```sql
-- Explain query plans to verify index usage
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM chat_messages 
WHERE session_id = 'abc123' 
ORDER BY timestamp DESC 
LIMIT 20;

-- Monitor index usage
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE tablename IN ('chat_sessions', 'chat_messages', 'calendar_events');
```

## Data Retention Policies

### Cleanup Procedures

```python
class DataRetentionManager:
    @staticmethod
    def cleanup_old_sessions(days_old: int = 30):
        """Remove sessions older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        old_sessions = ChatSession.query.filter(
            ChatSession.created_at < cutoff_date
        ).all()
        
        for session in old_sessions:
            db.session.delete(session)  # Cascade will handle messages
        
        db.session.commit()
        return len(old_sessions)
    
    @staticmethod
    def cleanup_orphaned_agent_states():
        """Remove agent states for non-existent sessions"""
        orphaned_states = db.session.query(AgentState)\
            .outerjoin(ChatSession, AgentState.session_id == ChatSession.session_id)\
            .filter(ChatSession.session_id.is_(None)).all()
        
        for state in orphaned_states:
            db.session.delete(state)
        
        db.session.commit()
        return len(orphaned_states)
```

## Backup and Recovery

### Backup Strategy

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/assistant_db"
DB_NAME="assistant_db"

# Create backup
pg_dump -h localhost -U assistant_user -d $DB_NAME \
    --verbose --no-password --format=custom \
    > $BACKUP_DIR/backup_$DATE.dump

# Compress backup
gzip $BACKUP_DIR/backup_$DATE.dump

# Remove backups older than 30 days
find $BACKUP_DIR -name "backup_*.dump.gz" -mtime +30 -delete
```

### Recovery Procedures

```bash
# Restore from backup
pg_restore -h localhost -U assistant_user -d assistant_db_new \
    --verbose --clean --if-exists backup_20250609_120000.dump

# Point-in-time recovery (if WAL archiving is enabled)
pg_basebackup -h localhost -D /var/lib/postgresql/recovery \
    -U assistant_user -v -P -W
```

This comprehensive database schema supports the multi-agent system's requirements for conversation management, agent state persistence, and calendar functionality while maintaining good performance and data integrity.