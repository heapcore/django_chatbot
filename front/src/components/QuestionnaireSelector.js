import React, { Component } from "react";

class QuestionnaireSelector extends Component {
  constructor() {
    super();
    this.state = {
      error: null,
      isLoaded: false,
      items: [],
      questionnaireId: "",
    };
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  componentDidMount() {
    fetch("http://127.0.0.1:8000/chat/questionnaires/")
      .then((res) => res.json())
      .then(
        (res) => {
          const firstId = res.length ? String(res[0].id) : "";
          this.setState({
            isLoaded: true,
            items: res,
            questionnaireId: firstId,
          });
        },
        (error) => {
          this.setState({
            isLoaded: true,
            error,
          });
        }
      );
  }

  handleChange(e) {
    this.setState({
      questionnaireId: e.target.value,
    });
  }

  handleSubmit(e) {
    e.preventDefault();
    if (!this.state.questionnaireId) {
      return;
    }
    this.props.startChat(Number(this.state.questionnaireId));
  }

  render() {
    if (this.state.error) {
      return <p>Failed to load questionnaires.</p>;
    }

    return (
      <form onSubmit={this.handleSubmit} className="select-questionnaire-form">
        <p>Please select the questionnaire: </p>
        <select size="1" value={this.state.questionnaireId} onChange={this.handleChange}>
          {this.state.items.map((item) => (
            <option key={item.id} value={item.id}>
              {item.name}
            </option>
          ))}
        </select>
        <input value="Start" type="submit" disabled={!this.state.questionnaireId} />
      </form>
    );
  }
}

export default QuestionnaireSelector;
