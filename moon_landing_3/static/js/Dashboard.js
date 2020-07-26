import Grid from "@material-ui/core/Grid";
import Paper from "@material-ui/core/Paper";
import Chart from "./Chart";
import Deposits from "./Deposits";
import Orders from "./Orders";
import React from "react";
import Typography from "@material-ui/core/Typography";
import Link from "@material-ui/core/Link";



function Copyright() {
  return (
    <Typography variant="body2" color="textSecondary" align="center">
      {'Copyright © '}
      <Link color="inherit" href="https://project-moon-landing.appspot.com/">
        Moon Landing
      </Link>{' '}
      {new Date().getFullYear()}
      {'.'}
    </Typography>
  );
}


class Dashboard extends React.Component {

  constructor() {
    super();
      this.state = {
        holdings: [],
        transactions: [],
        daily_data_chart: [],
        daily_gain: 1,
        isLoading: true,
      }
  }

    componentDidMount() {
        // TODO: there has to be a better way to get the account id for this than from the URL
      fetch(`/account_data/`+ window.location.href.substring(window.location.href.lastIndexOf('/') + 1))
        // We get the API response and receive data in JSON format...
        .then(response => response.json())
        // ...then we update the users state
        .then(data =>
          this.setState({
            holdings: data['positions'],
            transactions: data['transactions'],
            daily_data_chart: data['daily_data_chart'],
            daily_gain: data['week_gain'],
            isLoading: false,
          })
        )
        // Catch any errors we hit and update the app
        .catch(error => this.setState({ error, isLoading: false }));
    }

  render() {
    const { holdings, transactions, isLoading, daily_data_chart, daily_gain } = this.state;
    return (
    <React.Fragment>
          <Grid container spacing={3}>
            {/* Chart */}
            <Grid item xs={12} md={12} lg={6}>
              <Paper style={{ padding: "10px", display: 'flex', overflow: 'auto', flexDirection: 'column', height: "240px" }}>
                <Chart chartdata={daily_data_chart} daily_gain={daily_gain}/>
              </Paper>
            </Grid>
            {/* Recent Transactions */}
            <Grid item xs={12} md={12} lg={6}>
              <Paper style={{ padding: "10px", display: 'flex', overflow: 'auto', flexDirection: 'column', height: "240px" }}>
                <Deposits transactions={transactions}/>
              </Paper>
            </Grid>
            {/* Portfolio table */}
            <Grid item xs={12}>
              <Paper style={{ padding: "10px", display: 'flex', overflow: 'auto', flexDirection: 'column' }}>
                <Orders my_hold={holdings}/>
              </Paper>
            </Grid>
          </Grid>
      </React.Fragment>
        )
  }
}

export default Dashboard;