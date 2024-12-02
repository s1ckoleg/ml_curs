export interface NginxLog {
  timestamp: string;
  method: string;
  url: string;
  statusCode: number;
  bodyBytes: number;
  host: string;
}

export function parseNginxLog(log: string): NginxLog | null {
  const regex =
    /^(?:(\d+\.\d+\.\d+\.\d+)) - - \[([^\]]+)\] "([A-Z]+) ([^\s]+) HTTP\/[\d\.]+" (\d{3}) (\d+)$/;

  const match = log.match(regex);

  if (match) {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const [_, host, timestamp, method, url, statusCode, bodyBytes] = match;

    return {
      timestamp,
      method,
      url,
      statusCode: parseInt(statusCode, 10),
      bodyBytes: parseInt(bodyBytes, 10),
      host,
    };
  }

  return null;
}
