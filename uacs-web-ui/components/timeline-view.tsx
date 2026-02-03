'use client';

import { useState, useEffect } from 'react';
import { 
  ClockCounterClockwise, 
  ChatCircle, 
  User, 
  Wrench,
  Lightbulb,
  Spinner
} from '@phosphor-icons/react';
import { Card, CardContent, CardDescription, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { getConversations, getConversationTimeline, ApiError } from '@/lib/api';
import type { Conversation, TimelineEvent } from '@/lib/types';
import { toast } from 'sonner';
import { cn, formatRelativeTime } from '@/lib/utils';

export function TimelineView() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedSessionId, setSelectedSessionId] = useState<string>('');
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [timelineLoading, setTimelineLoading] = useState(false);
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  // Load conversations on mount
  useEffect(() => {
    loadConversations();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Load timeline when session selected
  useEffect(() => {
    if (selectedSessionId) {
      loadTimeline(selectedSessionId);
    }
  }, [selectedSessionId]);

  const loadConversations = async () => {
    setLoading(true);
    try {
      const data = await getConversations(0, 50);
      setConversations(data.conversations);
      
      // Auto-select first conversation
      if (data.conversations.length > 0 && !selectedSessionId) {
        setSelectedSessionId(data.conversations[0].session_id);
      }
    } catch (error) {
      if (error instanceof ApiError) {
        toast.error('Failed to load conversations', {
          description: error.message,
        });
      } else {
        toast.error('Network error');
      }
    } finally {
      setLoading(false);
    }
  };

  const loadTimeline = async (sessionId: string) => {
    setTimelineLoading(true);
    try {
      const data = await getConversationTimeline(sessionId);
      setTimeline(data.timeline);
    } catch (error) {
      if (error instanceof ApiError) {
        toast.error('Failed to load timeline', {
          description: error.message,
        });
      } else {
        toast.error('Network error');
      }
      setTimeline([]);
    } finally {
      setTimelineLoading(false);
    }
  };

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'user_message':
        return <User size={20} weight="bold" />;
      case 'assistant_message':
        return <ChatCircle size={20} weight="bold" />;
      case 'tool_use':
        return <Wrench size={20} weight="bold" />;
      default:
        return <Lightbulb size={20} weight="bold" />;
    }
  };

  const getEventColor = (type: string) => {
    switch (type) {
      case 'user_message':
        return 'bg-blue-500';
      case 'assistant_message':
        return 'bg-green-500';
      case 'tool_use':
        return 'bg-orange-500';
      default:
        return 'bg-purple-500';
    }
  };

  const getEventLabel = (type: string) => {
    switch (type) {
      case 'user_message':
        return 'User Message';
      case 'assistant_message':
        return 'Assistant Response';
      case 'tool_use':
        return 'Tool Use';
      default:
        return type.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase());
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <Spinner className="animate-spin text-teal-600 mb-4" size={32} />
        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          Loading conversations...
        </p>
      </div>
    );
  }

  if (conversations.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <ClockCounterClockwise size={48} className="text-zinc-400 mb-4" />
          <p className="text-lg font-medium text-zinc-900 dark:text-zinc-100">
            No conversations found
          </p>
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            Start a conversation to see it here
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">
          Conversation Timeline
        </h2>
        <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
          View chronological events from conversations
        </p>
      </div>

      {/* Session Selector */}
      <div className="flex flex-col gap-2">
        <label className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
          Select Conversation
        </label>
        <Select 
          value={selectedSessionId} 
          onValueChange={(value) => value && setSelectedSessionId(value)}
        >
          <SelectTrigger className="w-full max-w-xl">
            <SelectValue placeholder="Choose a conversation..." />
          </SelectTrigger>
          <SelectContent>
            {conversations.map((conv) => (
              <SelectItem key={conv.session_id} value={conv.session_id}>
                <div className="flex items-center justify-between gap-4 w-full">
                  <span className="truncate">{conv.session_id.slice(0, 8)}...</span>
                  <span className="text-xs text-zinc-500">
                    {conv.turn_count} turns • {conv.message_count} messages
                  </span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Timeline */}
      {timelineLoading ? (
        <div className="flex items-center justify-center py-12">
          <Spinner className="animate-spin text-teal-600" size={32} />
        </div>
      ) : timeline.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <ClockCounterClockwise size={48} className="text-zinc-400 mb-4" />
            <p className="text-lg font-medium text-zinc-900 dark:text-zinc-100">
              No events in this conversation
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="relative">
          {/* Timeline line */}
          <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-zinc-200 dark:bg-zinc-800" />
          
          {/* Events */}
          <div className="flex flex-col gap-4">
            {timeline.map((event, index) => (
              <div key={index} className="relative pl-12">
                {/* Timeline dot */}
                <div
                  className={cn(
                    'absolute left-2 top-6 h-5 w-5 rounded-full flex items-center justify-center text-white',
                    getEventColor(event.type)
                  )}
                >
                  {getEventIcon(event.type)}
                </div>

                {/* Event card */}
                <Card 
                  className="hover:shadow-md transition-shadow cursor-pointer"
                  onClick={() => setExpandedIndex(expandedIndex === index ? null : index)}
                >
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge className={cn('text-white', getEventColor(event.type))}>
                            {getEventLabel(event.type)}
                          </Badge>
                          <Badge variant="outline">
                            Turn {event.turn}
                          </Badge>
                          {event.tool_name && (
                            <Badge variant="outline" className="font-mono text-xs">
                              {event.tool_name}
                            </Badge>
                          )}
                          {event.latency_ms && (
                            <Badge variant="outline" className="text-xs">
                              {event.latency_ms}ms
                            </Badge>
                          )}
                        </div>
                        <CardDescription className="text-xs">
                          {formatRelativeTime(event.timestamp)}
                        </CardDescription>
                      </div>
                    </div>
                  </CardHeader>

                  {expandedIndex === index && event.content && (
                    <CardContent className="pt-0">
                      <div className="rounded-md bg-zinc-50 dark:bg-zinc-900 p-4">
                        <p className="text-sm text-zinc-700 dark:text-zinc-300 whitespace-pre-wrap">
                          {event.content}
                        </p>
                      </div>
                    </CardContent>
                  )}
                </Card>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
