import {Thread} from "@/components/assistant-ui/thread";
import {ThreadList} from "@/components/assistant-ui/thread-list";
import {useThread} from "@/contexts/ThreadContext";
import {
  AssistantRuntimeProvider,
  useLocalRuntime,
  type ChatModelAdapter
} from "@assistant-ui/react";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

const createModelAdapter = (
  setThreadId: (threadId: string | null) => void
): ChatModelAdapter => ({
  async run({messages, abortSignal}) {
    try {
      const result = await fetch(`${BACKEND_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          // @ts-ignore
          message: messages[messages.length - 1].content[0].text
          // No need for full messages or tool here, since backend handles everything
        }),
        signal: abortSignal
      });

      if (!result.ok) {
        throw new Error(`API error: ${result.statusText}`);
      }

      const data = await result.json();
      if (data.thread_id) {
        // Save thread ID to context
        setThreadId(data.thread_id);
      }

      console.log(data);

      if (data.questions) {
        console.log(data);
      }

      return {
        content: [
          {
            type: "text",
            text: data.message || data.detail || "No message from the chat",
            questions: data.questions
          }
        ]
      };
    } catch (error) {
      console.error(error);
      return {
        content: [{type: "text", text: "Error: " + (error as Error).message}]
      };
    }
  }
});

export default function Chat() {
  const {setThreadId} = useThread();
  const runtime = useLocalRuntime(createModelAdapter(setThreadId));

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <div>
        <ThreadList />
        <Thread />
      </div>
    </AssistantRuntimeProvider>
  );
}
