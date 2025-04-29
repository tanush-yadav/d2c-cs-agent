/**
 * Logger utility for structured logging
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  context?: Record<string, unknown>;
}

/**
 * A simple structured logger that outputs JSON format logs
 */
class Logger {
  private readonly namespace: string;

  constructor(namespace: string) {
    this.namespace = namespace;
  }

  /**
   * Log at debug level
   */
  debug(message: string, context?: Record<string, unknown>): void {
    this.log('debug', message, context);
  }

  /**
   * Log at info level
   */
  info(message: string, context?: Record<string, unknown>): void {
    this.log('info', message, context);
  }

  /**
   * Log at warn level
   */
  warn(message: string, context?: Record<string, unknown>): void {
    this.log('warn', message, context);
  }

  /**
   * Log at error level
   */
  error(message: string, context?: Record<string, unknown>): void {
    this.log('error', message, context);
  }

  /**
   * Format and output the log entry
   */
  private log(level: LogLevel, message: string, context?: Record<string, unknown>): void {
    // Don't log debug messages in production
    if (level === 'debug' && process.env.NODE_ENV === 'production') {
      return;
    }

    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message: `[${this.namespace}] ${message}`,
      ...(context && { context }),
    };

    // In production, output JSON for easier parsing
    if (process.env.NODE_ENV === 'production') {
      console[level === 'debug' ? 'log' : level](JSON.stringify(entry));
    } else {
      // In development, output a more readable format
      const contextStr = context ? ` ${JSON.stringify(context)}` : '';
      console[level === 'debug' ? 'log' : level](`${entry.timestamp} [${level.toUpperCase()}] ${entry.message}${contextStr}`);
    }
  }
}

export default Logger;