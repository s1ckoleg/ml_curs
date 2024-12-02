"use client";

import { fetchLog } from "@/lib/fetch-log";
import { useActionState, useState } from "react";
import { Button } from "./ui/button";
import { useFormStatus } from "react-dom";
import { Input } from "./ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Alert, AlertDescription, AlertTitle } from "./ui/alert";
import { AlertCircle, SendIcon, Terminal } from "lucide-react";
import { cn } from "@/lib/utils";
import { parseNginxLog } from "@/lib/parse-log";

type State = Partial<{
  message: string;
  result: number;
  payload: string;
}>;

const initialState: State = {
  message: undefined,
};

export async function checkLogAnomaly(
  state: any,
  formData: FormData | null,
): Promise<State | null> {
  if (formData === null) {
    return null;
  }

  return fetchLog(formData?.get("data") as string);
}

const SubmitButton = () => {
  const { pending } = useFormStatus();

  return (
    <Button
      type="submit"
      aria-disabled={pending}
      disabled={pending}
      className="flex items-center gap-2"
    >
      <SendIcon />
      Check
    </Button>
  );
};

export default function Form() {
  const [state, dispatch, isPending] = useActionState(
    checkLogAnomaly,
    initialState,
  );

  const [data, setData] = useState("");
  const parsedData = parseNginxLog(data);

  return (
    <>
      <Card className="max-w-lg w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <svg
              width="32px"
              height="32px"
              viewBox="0 0 32 32"
              xmlns="http://www.w3.org/2000/svg"
            >
              <title>file_type_nginx</title>
              <path
                d="M15.948,2h.065a10.418,10.418,0,0,1,.972.528Q22.414,5.65,27.843,8.774a.792.792,0,0,1,.414.788c-.008,4.389,0,8.777-.005,13.164a.813.813,0,0,1-.356.507q-5.773,3.324-11.547,6.644a.587.587,0,0,1-.657.037Q9.912,26.6,4.143,23.274a.7.7,0,0,1-.4-.666q0-6.582,0-13.163a.693.693,0,0,1,.387-.67Q9.552,5.657,14.974,2.535c.322-.184.638-.379.974-.535"
                fill="#00000"
              />
              <path
                d="M8.767,10.538q0,5.429,0,10.859a1.509,1.509,0,0,0,.427,1.087,1.647,1.647,0,0,0,2.06.206,1.564,1.564,0,0,0,.685-1.293c0-2.62-.005-5.24,0-7.86q3.583,4.29,7.181,8.568a2.833,2.833,0,0,0,2.6.782,1.561,1.561,0,0,0,1.251-1.371q.008-5.541,0-11.081a1.582,1.582,0,0,0-3.152,0c0,2.662-.016,5.321,0,7.982-2.346-2.766-4.663-5.556-7-8.332A2.817,2.817,0,0,0,10.17,9.033,1.579,1.579,0,0,0,8.767,10.538Z"
                fill="#ffffff"
              />
            </svg>
            NGINX Anomaly Detection
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form className="w-full flex items-center gap-4" action={dispatch}>
            <Input
              placeholder="Enter your log string"
              name="data"
              id="data"
              className="flex-1 flex"
              defaultValue={state?.payload}
              disabled={isPending}
              value={data}
              onChange={(e) => setData(e.target.value)}
            />
            <SubmitButton />
          </form>
        </CardContent>
      </Card>
      {parsedData ? (
        <Card className="max-w-lg w-full">
          <CardHeader>
            <CardTitle>Your Input</CardTitle>
          </CardHeader>
          <CardContent>
            <blockquote>
              <pre className="w-full">
                {JSON.stringify(parseNginxLog(data), null, 2)}
              </pre>
            </blockquote>
          </CardContent>
        </Card>
      ) : null}
      {state?.message && state?.payload === data ? (
        <Alert variant="destructive" className="max-w-lg w-full">
          <AlertCircle className="w-4 h-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{state.message}</AlertDescription>
        </Alert>
      ) : null}
      {state?.result !== undefined && data ? (
        <Alert
          variant={state.result === 0 ? "success" : "destructive"}
          className="max-w-lg w-full"
        >
          <Terminal
            className={cn(
              "h-4 w-4",
              state.result === 0 ? "text-green-500" : "text-destructive",
            )}
          />
          <AlertTitle>{state.result === 0 ? "Normal!" : "Anomaly!"}</AlertTitle>
          <AlertDescription>
            {state.result === 0
              ? "We believe that your log is absolutely normal. Nothing to worry about."
              : "Our very deep and smart neural network considered your log as anomalious."}
          </AlertDescription>
        </Alert>
      ) : null}
    </>
  );
}
