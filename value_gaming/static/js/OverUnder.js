import React from 'react';
import Card from 'react-bootstrap/Card';
import Button from "react-bootstrap/Button";

class OverUnder extends React.Component {

  constructor() {
    super();
      this.state = {
        isLoading: true,
        bets: [],
        error: false
      }
  }

    componentDidMount() {
        // Where we're fetching data from
      fetch(`/overunder_value`)
        .then(response => response.json())
        .then(data =>
          this.setState({
            bets: data,
            isLoading: false,
            error: false
          })
        )
        .catch(error => this.setState({ error, isLoading: false }));
    }
  render() {
    const { isLoading, bets, error } = this.state;
    return (
        <React.Fragment>
            {bets.map((bet, index) => (
                <Card key={index}>
                  <Card.Header>{bet.name}</Card.Header>
                  <Card.Body>
                    <Card.Title>{bet.home_team}  vs. {bet.away_team}</Card.Title>
                    <Card.Text>
                      Current Bet Value: {bet.value}
                    </Card.Text>
                    <Button variant="outline-info">View Details</Button>
                  </Card.Body>
                </Card>
            ))}
        </React.Fragment>
    );
  }
}
export default OverUnder;