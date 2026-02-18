import React, { Component } from "react";
import Title from "./components/Title.js";
import MessageList from "./components/MessageList.js";
import SendMessageForm from "./components/SendMessageForm.js";
import "./App.css";
import QuestionnaireSelector from "./components/QuestionnaireSelector";

class App extends Component {
  constructor() {
    super();
    this.state = {
      messages: [],
      sessionId: null,
      question: null,
      completed: false,
      error: null,
    };

    this.startChat = this.startChat.bind(this);
    this.submitAnswer = this.submitAnswer.bind(this);
  }

  startChat(questionnaireId) {
    fetch("http://127.0.0.1:8000/chat/start/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ questionnaire_id: questionnaireId }),
    })
      .then((res) => res.json())
      .then((res) => {
        if (!res.question) {
          throw new Error("Invalid response");
        }
        this.setState({
          sessionId: res.session_id,
          question: res.question,
          completed: Boolean(res.completed),
          error: null,
          messages: [{ type: "out", text: res.question.text }],
        });
      })
      .catch(() => {
        this.setState({ error: "Failed to start chat session." });
      });
  }

  submitAnswer(answer) {
    const currentQuestion = this.state.question;
    if (!currentQuestion) {
      return;
    }

    this.setState((prev) => ({
      messages: [...prev.messages, { type: "in", text: answer }],
    }));

    fetch("http://127.0.0.1:8000/chat/answer/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: this.state.sessionId,
        question_id: currentQuestion.id,
        answer: answer,
      }),
    })
      .then((res) => res.json())
      .then((res) => {
        if (!res.question) {
          throw new Error("Invalid response");
        }
        this.setState((prev) => ({
          question: res.question,
          completed: Boolean(res.completed),
          messages: [...prev.messages, { type: "out", text: res.question.text }],
        }));
      })
      .catch(() => {
        this.setState({ error: "Failed to process answer." });
      });
  }

  render() {
    const { messages, question, completed, error } = this.state;
    const started = question !== null || messages.length > 0;

    return (
      <div className="app">
        <Title />
        {error ? <p style={{ paddingLeft: "15px", color: "red" }}>{error}</p> : null}

        {!started ? <QuestionnaireSelector startChat={this.startChat} /> : null}

        {started ? <MessageList messages={messages} /> : null}

        {started && !completed && question ? (
          <SendMessageForm answers={question.answers || []} submitAnswer={this.submitAnswer} />
        ) : null}
      </div>
    );
  }
}

export default App;
