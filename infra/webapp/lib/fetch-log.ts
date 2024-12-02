import { BASE_URL } from "./const";
import { parseNginxLog } from "./parse-log";

export async function fetchLog(logString: string) {
  try {
    const parsedLog = parseNginxLog(logString);

    if (!parsedLog) {
      throw new Error("Could not parse your log. Wrong format.");
    }

    const logObj = {
      timestamp: parsedLog?.timestamp,
      http: {
        request: {
          method: parsedLog?.method,
        },
        response: {
          status_code: parsedLog?.statusCode,
          body: {
            bytes: parsedLog?.bodyBytes,
          },
        },
      },
      url: {
        original: parsedLog?.url,
      },
      source: {
        address: parsedLog?.host,
      },
    };

    const response = await fetch(BASE_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(logObj),
    });

    const json = await response.json();

    if (!response.ok) {
      throw new Error(
        "Something went wrong asking our very smart neural network.",
      );
    }

    return {
      result: json.is_anomaly,
      payload: logString,
    };
  } catch (error) {
    return {
      message: (error as any).message,
      payload: logString,
    };
  }
}
