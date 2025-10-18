import {
  useLangGraphInterruptState,
  useLangGraphSendCommand
} from "@assistant-ui/react-langgraph";
import Questions from "./Questions";
import {Button} from "./ui/button";

export const InterruptUI = () => {
  const interrupt = useLangGraphInterruptState();
  const sendCommand = useLangGraphSendCommand();
  if (!interrupt) return null;

  const answers = {
    question: "question",
    answer: "answer"
  };

  /*************  ✨ Windsurf Command ⭐  *************/
  /**
   * Sends a command to LangGraph to resume the graph with the user's answer.
   * The answer is a JSON object with the question and answer.
   */
  /*******  b4458e7f-2f34-489a-82e2-dcdf6c1ce985  *******/ const respondYes =
    () => {
      sendCommand({resume: JSON.stringify(answers)});
    };
  const respondNo = () => {
    sendCommand({resume: "no"});
  };

  const questions = interrupt.value.questions;

  return (
    <div className="flex flex-col gap-2">
      <div>Interrupt: </div>
      <div>
        <Questions questions={questions} />
      </div>
      <div className="flex items-end gap-2">
        <Button onClick={respondYes}>Submit</Button>
        {/* <Button onClick={respondNo}>Reject</Button> */}
      </div>
    </div>
  );
};
