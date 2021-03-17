import GameCard from "./GameCard";
import React from "react";


class PastResults extends React.Component {

      constructor() {
        super();
          this.state = {
            isLoading: true,
            recent_games: [],
            error: false
          }
      }

    componentDidMount() {
        // Where we're fetching data from
      fetch(`/past_results`)
        .then(response => response.json())
        .then(data =>
          this.setState({
            recent_games: data['recent_games'],
            isLoading: false,
            error: false
          })
        )
        .catch(error => this.setState({ error, isLoading: false }));
    }
    render() {
        const { isLoading, recent_games, error } = this.state;
        console.log(recent_games);
        return (
            <div className="sub-container">
                {recent_games.map((bet, index) => (
                    <GameCard bet={bet} index={index} key={index} />
                    ))
                }
            </div>
        )
    }
}
export default PastResults;