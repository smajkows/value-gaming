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
        <div className="sub-container">
            {bets.map((bet, index) => (
                <Card key={index} className="margin-top-10">
                  <Card.Header>{bet.name}</Card.Header>
                  <Card.Body>
                    <Card.Title>{bet.home_team} {bet.home_team_score} vs. {bet.away_team} {bet.away_team_score}</Card.Title>
                    <Card.Text>
                        {<b>{bet.time ? `${bet.time} in the ${bet.period}` : 'Game not started'}</b>}
                    </Card.Text>
                    <Card.Text>
                      Current Bet Value: {bet.value ? `${bet.value}`: 'Unknown'}
                    </Card.Text>
                    <Button variant="outline-info">View Details</Button>
                  </Card.Body>
                </Card>
            ))}
        </div>
    );
  }
}
export default OverUnder;