import React from 'react';
import Card from 'react-bootstrap/Card';
import Button from "react-bootstrap/Button";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";


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
    if (isLoading){
        return (
            <div className="sub-container">
                <h1> LOADING </h1>
            </div>
        );
    }
    else if (bets.length === 0){
        return (
            <div className="sub-container">
                <Card> There are no live games, check back later. </Card>
            </div>
        );
    } else {
    return (
        <div className="sub-container">
            {bets.map((bet, index) => (
                <Card key={index} className="margin-top-10">
                  <Card.Header>{bet.name}</Card.Header>
                  <Card.Body>
                    <Container>
                          <Row>
                            <Col sm={10}>
                                <Card.Title> {bet.away_team} ({bet.away_team_score}) vs. {bet.home_team} ({bet.home_team_score})
                                </Card.Title>
                                <Card.Text> {bet.time ? `${bet.time} in the ${bet.period}` : 'Game not started'}</Card.Text>
                            </Col>
                            <Col sm={2}>
                                <Button variant="outline-info">View Details</Button>
                            </Col>
                          </Row>
                          <Row className="margin-top-10">
                            <Col>
                              <Card.Text>
                                  Moneyline:
                              </Card.Text>
                                <Card.Text>
                                    {bet['moneyline_plus'] ? `${bet['moneyline_plus']['odds']} | ${bet['moneyline_minus']['odds']}` : 'Not Avaliable'}
                                </Card.Text>
                            </Col>
                            <Col>
                              <Card.Text>
                                  Spreads:
                              </Card.Text>
                              <Card.Text>
                                  {bet['spread_plus'] ? `${bet['spread_plus']['line']} ${bet['spread_plus']['odds']}  | ${bet['spread_minus']['line']} ${bet['spread_minus']['odds']}` : 'Not Available'}
                              </Card.Text>
                            </Col>
                            <Col>
                              <Card.Text>
                                  O/U:
                              </Card.Text>
                              <Card.Text>
                                  {bet['O'] ? `Over: ${bet['O']['line']} ${bet['O']['odds']}  | Under:${bet['U']['line']} ${bet['U']['odds']}` : 'Not Available'}
                              </Card.Text>
                            </Col>
                          </Row>
                        </Container>

                  </Card.Body>
                </Card>
            ))}
        </div>
    );
    }
  }
}
export default OverUnder;