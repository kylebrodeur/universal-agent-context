'use client';

import { useState } from 'react';
import { MagnifyingGlass, Spinner } from '@phosphor-icons/react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { searchContent, ApiError } from '@/lib/api';
import type { SearchResult } from '@/lib/types';
import { toast } from 'sonner';
import { cn, formatRelativeTime } from '@/lib/utils';

const CONTENT_TYPES = [
  { value: 'user_message', label: 'User Messages', color: 'bg-blue-500' },
  { value: 'assistant_message', label: 'Assistant Messages', color: 'bg-green-500' },
  { value: 'tool_use', label: 'Tool Uses', color: 'bg-orange-500' },
  { value: 'decision', label: 'Decisions', color: 'bg-purple-500' },
  { value: 'convention', label: 'Conventions', color: 'bg-pink-500' },
  { value: 'learning', label: 'Learnings', color: 'bg-teal-500' },
  { value: 'artifact', label: 'Artifacts', color: 'bg-amber-500' },
];

export function SearchView() {
  const [query, setQuery] = useState('');
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!query.trim()) {
      toast.error('Please enter a search query');
      return;
    }

    setLoading(true);
    setSearched(true);
    setExpandedIndex(null);

    try {
      const data = await searchContent(
        query,
        selectedTypes.length > 0 ? selectedTypes : undefined,
        undefined,
        0.7,
        20
      );
      
      setResults(data.results);
      
      if (data.results.length === 0) {
        toast.info('No results found', {
          description: 'Try adjusting your search query or filters',
        });
      } else {
        toast.success(`Found ${data.count} results`);
      }
    } catch (error) {
      if (error instanceof ApiError) {
        toast.error('Search failed', {
          description: error.message,
        });
      } else {
        toast.error('Network error', {
          description: 'Could not connect to server',
        });
      }
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const toggleType = (type: string) => {
    setSelectedTypes((prev) =>
      prev.includes(type)
        ? prev.filter((t) => t !== type)
        : [...prev, type]
    );
  };

  const getTypeColor = (type: string) => {
    return CONTENT_TYPES.find((t) => t.value === type)?.color || 'bg-gray-500';
  };

  const getTypeLabel = (type: string) => {
    return CONTENT_TYPES.find((t) => t.value === type)?.label || type;
  };

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">
          Semantic Search
        </h2>
        <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
          Search across conversations, decisions, conventions, learnings, and artifacts
        </p>
      </div>

      {/* Search Form */}
      <form onSubmit={handleSearch} className="flex flex-col gap-4">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <MagnifyingGlass 
              className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400" 
              size={20} 
            />
            <Input
              type="text"
              placeholder="Search for concepts, decisions, patterns..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="pl-10"
              disabled={loading}
            />
          </div>
          <Button type="submit" disabled={loading}>
            {loading ? (
              <>
                <Spinner className="mr-2 animate-spin" size={16} />
                Searching...
              </>
            ) : (
              'Search'
            )}
          </Button>
        </div>

        {/* Type Filters */}
        <div className="flex flex-wrap gap-4">
          <Label className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
            Filter by type:
          </Label>
          {CONTENT_TYPES.map((type) => (
            <label
              key={type.value}
              className="flex items-center gap-2 cursor-pointer"
            >
              <input
                type="checkbox"
                checked={selectedTypes.includes(type.value)}
                onChange={() => toggleType(type.value)}
                className="h-4 w-4 rounded border-zinc-300 text-teal-600 focus:ring-teal-500"
                disabled={loading}
              />
              <span className="text-sm text-zinc-700 dark:text-zinc-300">
                {type.label}
              </span>
            </label>
          ))}
        </div>
      </form>

      {/* Results */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <Spinner className="animate-spin text-teal-600" size={32} />
        </div>
      )}

      {!loading && searched && results.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <MagnifyingGlass size={48} className="text-zinc-400 mb-4" />
            <p className="text-lg font-medium text-zinc-900 dark:text-zinc-100">
              No results found
            </p>
            <p className="text-sm text-zinc-600 dark:text-zinc-400">
              Try adjusting your search query or filters
            </p>
          </CardContent>
        </Card>
      )}

      {!loading && results.length > 0 && (
        <div className="flex flex-col gap-3">
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            Found {results.length} results
          </p>
          
          {results.map((result, index) => (
            <Card 
              key={index}
              className="hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => setExpandedIndex(expandedIndex === index ? null : index)}
            >
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge 
                        className={cn(
                          'text-white',
                          getTypeColor(result.type)
                        )}
                      >
                        {getTypeLabel(result.type)}
                      </Badge>
                      <Badge variant="outline">
                        {(result.similarity * 100).toFixed(0)}% match
                      </Badge>
                    </div>
                    <CardTitle className="text-base line-clamp-2">
                      {result.text.substring(0, 150)}
                      {result.text.length > 150 ? '...' : ''}
                    </CardTitle>
                  </div>
                </div>
              </CardHeader>
              
              {expandedIndex === index && (
                <CardContent className="pt-0">
                  <div className="rounded-md bg-zinc-50 dark:bg-zinc-900 p-4">
                    <p className="text-sm text-zinc-700 dark:text-zinc-300 whitespace-pre-wrap">
                      {result.text}
                    </p>
                    
                    {result.metadata && Object.keys(result.metadata).length > 0 && (
                      <div className="mt-4 pt-4 border-t border-zinc-200 dark:border-zinc-800">
                        <p className="text-xs font-medium text-zinc-500 dark:text-zinc-400 mb-2">
                          Metadata:
                        </p>
                        <div className="grid grid-cols-2 gap-2">
                          {Object.entries(result.metadata).map(([key, value]) => (
                            <div key={key} className="text-xs">
                              <span className="font-medium text-zinc-600 dark:text-zinc-400">
                                {key}:
                              </span>{' '}
                              <span className="text-zinc-700 dark:text-zinc-300">
                                {typeof value === 'string' && key.includes('timestamp')
                                  ? formatRelativeTime(value)
                                  : String(value)}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              )}
            </Card>
          ))}
        </div>
      )}

      {!loading && !searched && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <MagnifyingGlass size={48} className="text-zinc-400 mb-4" />
            <p className="text-lg font-medium text-zinc-900 dark:text-zinc-100">
              Start searching
            </p>
            <p className="text-sm text-zinc-600 dark:text-zinc-400">
              Enter a query to search across all UACS content
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
