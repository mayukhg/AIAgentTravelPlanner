import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy import and_, or_
from .base_agent import BaseAgent
from models import CalendarEvent
from app import db

class CalendarAgent(BaseAgent):
    """Specialized agent for calendar and scheduling operations"""
    
    def __init__(self, bedrock_service, tools_service=None):
        super().__init__("calendar_agent", bedrock_service, tools_service)
        
    def get_system_prompt(self) -> str:
        return """You are a Calendar Assistant AI specialized in scheduling and event management.

Your capabilities include:
- Creating, updating, and deleting calendar events
- Finding available time slots
- Scheduling meetings and appointments
- Managing recurring events
- Providing schedule summaries
- Handling time zone considerations
- Conflict detection and resolution

When processing calendar requests:
1. Parse dates and times accurately (handle various formats)
2. Consider the user's current time zone context
3. Check for scheduling conflicts
4. Provide clear confirmations for actions taken
5. Suggest alternatives when conflicts exist

Always be precise with date/time information and confirm important scheduling details with the user.

For event creation, you need: title, start time, end time, and optionally description and location.
Use appropriate date parsing for natural language like "tomorrow at 2 PM" or "next Friday morning"."""

    def can_handle(self, task: str, context: Dict[str, Any]) -> bool:
        """Determine if this is a calendar-related task"""
        calendar_keywords = [
            'schedule', 'calendar', 'meeting', 'appointment', 'event',
            'book', 'reserve', 'plan', 'date', 'time', 'when',
            'available', 'busy', 'free', 'tomorrow', 'today',
            'next week', 'monday', 'tuesday', 'wednesday', 'thursday',
            'friday', 'saturday', 'sunday', 'cancel', 'reschedule'
        ]
        
        task_lower = task.lower()
        return any(keyword in task_lower for keyword in calendar_keywords)
    
    async def process_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process calendar-related tasks"""
        try:
            # Analyze the task to determine the specific calendar action needed
            action_analysis = await self._analyze_calendar_action(task, context)
            
            action_type = action_analysis.get('action_type')
            
            if action_type == 'create_event':
                return await self._create_event(action_analysis, context)
            elif action_type == 'list_events':
                return await self._list_events(action_analysis, context)
            elif action_type == 'update_event':
                return await self._update_event(action_analysis, context)
            elif action_type == 'delete_event':
                return await self._delete_event(action_analysis, context)
            elif action_type == 'find_free_time':
                return await self._find_free_time(action_analysis, context)
            else:
                # General calendar query
                return await self._handle_general_query(task, context)
                
        except Exception as e:
            self.logger.error(f"Error processing calendar task: {str(e)}")
            return self.format_error(f"I encountered an error while managing your calendar: {str(e)}")
    
    async def _analyze_calendar_action(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the calendar task to determine specific action needed"""
        
        analysis_prompt = f"""Analyze this calendar request and extract structured information:

User Request: "{task}"

Determine the action type and extract relevant details. Respond with JSON in this format:
{{
    "action_type": "create_event|list_events|update_event|delete_event|find_free_time|general_query",
    "event_details": {{
        "title": "event title if creating/updating",
        "start_time": "parsed datetime in ISO format if specified",
        "end_time": "parsed datetime in ISO format if specified", 
        "description": "description if provided",
        "location": "location if provided",
        "all_day": true/false
    }},
    "query_parameters": {{
        "date_range_start": "start date for queries in ISO format",
        "date_range_end": "end date for queries in ISO format",
        "search_term": "search term for finding events"
    }},
    "reasoning": "explanation of the analysis"
}}

For date/time parsing:
- "tomorrow" = next day
- "next week" = following week
- Handle various natural language time expressions
- Default to 1-hour duration if end time not specified
- Use current date/time as reference: {datetime.now().isoformat()}

Action type guidelines:
- create_event: "schedule", "book", "add event", "create meeting"
- list_events: "what's on", "my schedule", "show events", "what do I have"
- update_event: "change", "modify", "reschedule", "update"
- delete_event: "cancel", "remove", "delete"
- find_free_time: "when am I free", "available times", "find time"
- general_query: other calendar-related questions"""

        try:
            messages = [{"role": "user", "content": analysis_prompt}]
            response = await self.generate_response(messages, max_tokens=500)
            
            analysis = json.loads(response.strip())
            return analysis
            
        except (json.JSONDecodeError, Exception) as e:
            self.logger.warning(f"Error analyzing calendar action: {str(e)}")
            return {
                "action_type": "general_query",
                "event_details": {},
                "query_parameters": {},
                "reasoning": "Unable to parse, treating as general query"
            }
    
    async def _create_event(self, analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new calendar event"""
        try:
            event_details = analysis.get('event_details', {})
            
            # Validate required fields
            if not event_details.get('title'):
                return self.format_error("I need a title for the event. Please specify what you'd like to schedule.")
            
            if not event_details.get('start_time'):
                return self.format_error("I need a start time for the event. Please specify when you'd like to schedule it.")
            
            # Parse datetime strings
            start_time = datetime.fromisoformat(event_details['start_time'].replace('Z', '+00:00'))
            
            # Set end time (default to 1 hour later if not specified)
            if event_details.get('end_time'):
                end_time = datetime.fromisoformat(event_details['end_time'].replace('Z', '+00:00'))
            else:
                end_time = start_time + timedelta(hours=1)
            
            # Check for conflicts
            conflicts = self._check_conflicts(start_time, end_time)
            if conflicts:
                conflict_info = ", ".join([f"{event.title} ({event.start_time.strftime('%H:%M')}-{event.end_time.strftime('%H:%M')})" for event in conflicts])
                return self.format_error(f"Time conflict detected with: {conflict_info}. Please choose a different time.")
            
            # Create the event
            event = CalendarEvent(
                title=event_details['title'],
                description=event_details.get('description', ''),
                start_time=start_time,
                end_time=end_time,
                location=event_details.get('location', ''),
                all_day=event_details.get('all_day', False)
            )
            
            db.session.add(event)
            db.session.commit()
            
            return self.format_response(
                f"✅ Event created successfully!\n\n"
                f"**{event.title}**\n"
                f"📅 {start_time.strftime('%A, %B %d, %Y')}\n"
                f"🕐 {start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}\n"
                + (f"📍 {event.location}\n" if event.location else "")
                + (f"📝 {event.description}" if event.description else ""),
                {
                    'event_id': event.id,
                    'event_data': event.to_dict(),
                    'action_performed': 'create_event'
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error creating event: {str(e)}")
            return self.format_error(f"Failed to create event: {str(e)}")
    
    async def _list_events(self, analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """List calendar events based on query parameters"""
        try:
            query_params = analysis.get('query_parameters', {})
            
            # Default to showing today's events if no range specified
            if not query_params.get('date_range_start'):
                start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                start_date = datetime.fromisoformat(query_params['date_range_start'].replace('Z', '+00:00'))
            
            if not query_params.get('date_range_end'):
                end_date = start_date + timedelta(days=1)
            else:
                end_date = datetime.fromisoformat(query_params['date_range_end'].replace('Z', '+00:00'))
            
            # Query events
            events_query = CalendarEvent.query.filter(
                and_(
                    CalendarEvent.start_time >= start_date,
                    CalendarEvent.start_time < end_date
                )
            ).order_by(CalendarEvent.start_time)
            
            events = events_query.all()
            
            if not events:
                date_str = start_date.strftime('%A, %B %d, %Y')
                return self.format_response(
                    f"📅 No events scheduled for {date_str}",
                    {'events': [], 'date_range': {'start': start_date.isoformat(), 'end': end_date.isoformat()}}
                )
            
            # Format events list
            events_text = f"📅 **Your Schedule for {start_date.strftime('%A, %B %d, %Y')}**\n\n"
            
            for event in events:
                time_str = event.start_time.strftime('%I:%M %p')
                if not event.all_day:
                    time_str += f" - {event.end_time.strftime('%I:%M %p')}"
                
                events_text += f"• **{event.title}**\n"
                events_text += f"  🕐 {time_str}\n"
                if event.location:
                    events_text += f"  📍 {event.location}\n"
                if event.description:
                    events_text += f"  📝 {event.description}\n"
                events_text += "\n"
            
            return self.format_response(
                events_text.strip(),
                {
                    'events': [event.to_dict() for event in events],
                    'date_range': {'start': start_date.isoformat(), 'end': end_date.isoformat()},
                    'action_performed': 'list_events'
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error listing events: {str(e)}")
            return self.format_error(f"Failed to retrieve events: {str(e)}")
    
    def _check_conflicts(self, start_time: datetime, end_time: datetime) -> List[CalendarEvent]:
        """Check for scheduling conflicts"""
        conflicts = CalendarEvent.query.filter(
            or_(
                and_(CalendarEvent.start_time <= start_time, CalendarEvent.end_time > start_time),
                and_(CalendarEvent.start_time < end_time, CalendarEvent.end_time >= end_time),
                and_(CalendarEvent.start_time >= start_time, CalendarEvent.end_time <= end_time)
            )
        ).all()
        
        return conflicts
    
    async def _update_event(self, analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing event"""
        # Implementation for updating events
        return self.format_response("Event update functionality is being implemented.")
    
    async def _delete_event(self, analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Delete an event"""
        # Implementation for deleting events
        return self.format_response("Event deletion functionality is being implemented.")
    
    async def _find_free_time(self, analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Find available time slots"""
        # Implementation for finding free time
        return self.format_response("Free time finder functionality is being implemented.")
    
    async def _handle_general_query(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general calendar queries"""
        try:
            messages = context.get('messages', [])
            messages.append({"role": "user", "content": task})
            
            response = await self.generate_response(messages)
            
            return self.format_response(response, {
                'action_performed': 'general_query'
            })
            
        except Exception as e:
            self.logger.error(f"Error handling general query: {str(e)}")
            return self.format_error(f"Failed to process query: {str(e)}")
    
    def get_capabilities(self) -> List[str]:
        """Return calendar agent capabilities"""
        return [
            "Create and manage calendar events",
            "Schedule meetings and appointments", 
            "Check availability and find free time slots",
            "Handle date/time parsing in natural language",
            "Detect and resolve scheduling conflicts",
            "Provide schedule summaries and reminders"
        ]
