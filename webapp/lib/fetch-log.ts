interface NginxLog {
  timestamp: string;
  method: string;
  url: string;
  statusCode: number;
  bodyBytes: number;
  host: string;
}

function parseNginxLog(log: string): NginxLog | null {
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

export async function fetchLog(logString: string) {
  try {
    const parsedLog = parseNginxLog(logString);

    if (!parsedLog) {
      throw new Error();
    }

    const logObj = {
      timestamp: parsedLog.timestamp,
      http: {
        request: {
          method: parsedLog.method,
        },
        response: {
          status_code: parsedLog.statusCode,
          body: {
            bytes: parsedLog.bodyBytes,
          },
        },
      },
      url: {
        original: parsedLog.url,
      },
      source: {
        address: parsedLog.host,
      },
    };

    const response = await fetch("https://api.thesmolentsev.ru/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(logObj),
    });

    const json = await response.json();

    if (!response.ok) {
      console.error("Error sending message: ", json);
      throw new Error();
    }

    return {
      logObj: JSON.stringify(logObj),
      result: json.is_anomaly,
      payload: logString,
    };
  } catch {
    return {
      message: "Could not verify your log. Please check if it is valid.",
      payload: logString,
    };
  }
}
