import React from 'react';
import Card from 'react-bootstrap/Card';
import Button from "react-bootstrap/Button";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";


class GameCard extends React.Component {
  render() {
    const bet = this.props.bet;
    return(
        <Card key={this.props.index} className="margin-top-10">
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
                            {bet.moneyline_plus_odds ? `${bet.moneyline_plus_odds} | ${bet.moneyline_minus_odds}` : 'Not Avaliable'}
                        </Card.Text>
                    </Col>
                    <Col>
                      <Card.Text>
                          Spreads:
                      </Card.Text>
                      <Card.Text>
                          {bet.spread_line ? `+${bet.spread_line} ${bet.spread_plus_odds}  | -${bet.spread_line} ${bet.spread_minus_odds}` : 'Not Available'}
                      </Card.Text>
                    </Col>
                    <Col>
                      <Card.Text>
                          O/U:
                      </Card.Text>
                      <Card.Text>
                          {bet.over_under_line ? `Over ${bet.over_under_line}: ${bet.over_under_O_odds}  | Under ${bet.over_under_line}:${bet.over_under_U_odds}` : 'Not Available'}
                      </Card.Text>
                    </Col>
                  </Row>
                </Container>
          </Card.Body>
        </Card>
    );
  }
}
export default GameCard;