import React, { Component } from "react";

class SendMessageForm extends Component {
  constructor() {
    super();
    this.state = {
      answer: "",
    };
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  componentDidUpdate(prevProps) {
    if (prevProps.answers !== this.props.answers) {
      const nextDefault = this.props.answers.length ? this.props.answers[0] : "";
      this.setState({ answer: nextDefault });
    }
  }

  handleChange(e) {
    this.setState({
      answer: e.target.value,
    });
  }

  handleSubmit(e) {
    e.preventDefault();
    if (!this.state.answer) {
      return;
    }
    this.props.submitAnswer(this.state.answer);
  }

  render() {
    if (!this.props.answers.length) {
      return null;
    }

    return (
      <form onSubmit={this.handleSubmit} className="send-message-form">
        <select value={this.state.answer} onChange={this.handleChange}>
          {this.props.answers.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
        <input value="Send" type="submit" />
      </form>
    );
  }
}

export default SendMessageForm;
