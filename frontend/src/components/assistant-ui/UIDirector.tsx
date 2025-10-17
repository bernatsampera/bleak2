import {cn} from "@/lib/utils";
import {
  MarkdownTextPrimitive,
  unstable_memoizeMarkdownComponents as memoizeMarkdownComponents
} from "@assistant-ui/react-markdown";
import {memo} from "react";
import remarkGfm from "remark-gfm";
import Questions from "../Questions";

const UiDirectorImpl = (props: any) => {
  const tool_used = props.tool_used;
  const topic = props.topic;

  console.log("props", props);

  if (props.questions) {
    const questionWithIds = props.questions.map((q: any) => {
      return {
        ...q,
        id: q.question.substr(0, 30).replace(/[^a-zA-Z0-9]/g, "_")
      };
    });

    return <Questions questions={questionWithIds} />;
  }

  // if (tool_used) {
  //   switch (tool_used.name) {
  //     case "list_document":
  //       return (
  //         <DisplayDocumentReferences
  //           document_references={tool_used.result}
  //           topicName={topic.name}
  //         />
  //       );
  //     case "list_explanation":
  //       // Directing using the docs references from the topic, would be better if they come from the explanation tool (trying how it works)
  //       return (
  //         <ExplanationPanel
  //           explanation={tool_used.result}
  //           document_references={topic.document_references}
  //         />
  //       );
  //     default:
  //       return (
  //         <MarkdownTextPrimitive
  //           remarkPlugins={[remarkGfm]}
  //           className="aui-md"
  //           components={defaultComponents}
  //         />
  //       );
  //   }
  // }

  return (
    <MarkdownTextPrimitive
      remarkPlugins={[remarkGfm]}
      className="aui-md"
      components={defaultComponents}
    />
  );
};

export const UIDirector = memo(UiDirectorImpl);

const defaultComponents = memoizeMarkdownComponents({
  h2: ({className, ...props}) => (
    <h1
      className={cn(
        "mb-8 scroll-m-20 text-4xl font-extrabold tracking-tight last:mb-0",
        className
      )}
      {...props}
    />
  )
});
