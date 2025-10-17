import {useThread} from "@/contexts/ThreadContext";
import {useState} from "react";

type QuestionType = {
  question: string;
  type: "input" | "radio";
  options?: string[];
  id: string;
};

interface Answer {
  question: string;
  answer: string;
}

interface QuestionsProps {
  questions: QuestionType[];
  onAnswersChange?: (answers: Record<string, string>) => void;
}

export default function Questions({
  questions,
  onAnswersChange
}: QuestionsProps) {
  const {threadId} = useThread();
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  console.log(answers);
  const handleInputChange = (questionId: string, value: string) => {
    const newAnswers = {...answers, [questionId]: value};
    setAnswers(newAnswers);
    onAnswersChange?.(newAnswers);
  };

  const handleSubmitAnswers = async () => {
    setIsSubmitting(true);

    try {
      // Format answers as required by backend
      const formattedAnswers: Answer[] = questions.map((question) => ({
        question: question.question,
        answer: answers[question.id] || ""
      }));

      // Submit answers through the utility - this will automatically trigger
      // the chat adapter to process the submission
      if (threadId) {
        // submitAnswers(formattedAnswers, threadId);
        console.log("Answers submitted for processing");
      } else {
        console.error("No thread ID available for answer submission");
      }
    } catch (error) {
      console.error("Error submitting answers:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderQuestion = (question: QuestionType) => {
    switch (question.type) {
      case "input":
        return (
          <input
            type="text"
            placeholder="Type your answer..."
            className="input input-bordered input-sm w-full max-w-xs"
            value={answers[question.id] || ""}
            onChange={(e) => handleInputChange(question.id, e.target.value)}
          />
        );
      case "radio":
        return (
          <div className="space-y-2">
            {question.options?.map((option) => (
              <label key={option} className="label cursor-pointer">
                <span className="label-text">{option}</span>
                <input
                  type="radio"
                  name={question.id}
                  className="radio radio-sm"
                  value={option}
                  checked={answers[question.id] === option}
                  onChange={(e) =>
                    handleInputChange(question.id, e.target.value)
                  }
                />
              </label>
            ))}
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {questions.map((question: QuestionType) => (
        <div key={question.question} className="form-control w-full max-w-md">
          <label className="label">
            <span className="label-text font-medium">{question.question}</span>
          </label>
          render {renderQuestion(question)}
        </div>
      ))}
      <div className="form-control w-full max-w-md">
        <button
          onClick={handleSubmitAnswers}
          disabled={isSubmitting || Object.keys(answers).length === 0}
          className="btn btn-primary"
        >
          {isSubmitting ? "Submitting..." : "Submit Answers"}
        </button>
      </div>
    </div>
  );
}
