import Grid from "@material-ui/core/Grid";
import Paper from "@material-ui/core/Paper";
import TableContainer from "@material-ui/core/TableContainer";
import Chart from "./Chart";
import Deposits from "./Deposits";
import Orders from "./Orders";
import Button from "@material-ui/core/Button";
import React from "react";
import Typography from "@material-ui/core/Typography";
import Link from "@material-ui/core/Link";
import Title from "./Title";
import axios from "axios";
import Cookies from "js-cookie";
import CurrencyFormat from "react-currency-format";

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
        follow_status: false,
        current_balance: 0,
        account_id: '',
        account_name: '',
        daily_gain: 1,
        isLoading: true,
      }
        this.follow = this.follow.bind(this);
        this.unfollow = this.unfollow.bind(this);
  }

  follow(e) {
      e.stopPropagation();
      const csrftoken = Cookies.get('csrftoken');
      const token = Cookies.get('token');
        axios.post('/follow/account',
          {
            target_account_id: this.state.account_id,
            follow_action: 'follow',
            firebase_token: token
            },
           {
               headers: {
                'X-CSRFToken': csrftoken
               }
          }).then(response =>
              this.setState({
                follow_status: response['data']['follow_status'],
                follower_count: response['data']['follower_count']
            })
          );
    }


  unfollow(e){
      e.stopPropagation();
      const csrftoken = Cookies.get('csrftoken');
      const token = Cookies.get('token');
        axios.post('/follow/account',
          {
            target_account_id: this.state.account_id,
            follow_action: 'unfollow',
            firebase_token: token
            },
           {
               headers: {
                'X-CSRFToken': csrftoken
               }
          }).then(response =>
              this.setState({
                follow_status: response['data']['follow_status'],
                follower_count: response['data']['follower_count']
            })
          );
  }

    componentDidMount() {
        // TODO: there has to be a better way to get the account id for this than from the URL
      fetch(`/account_data/`+ window.location.href.substring(window.location.href.lastIndexOf('/') + 1))
        // We get the API response and receive data in JSON format...
        .then(response => response.json())
        // ...then we update the users state
        .then(data =>
          this.setState({
            holdings: data['positions'].reverse(),
            follower_count: data['followers'],
            transactions: data['transactions'],
            account_id: data['account_id'],
            daily_data_chart: data['daily_data_chart'],
            current_balance: data['current_balance'],
            daily_gain: data['week_gain'],
            account_name: data['account_name'],
            follow_status: data['follow_status'],
            isLoading: false,
          })
        )
        // Catch any errors we hit and update the app
        .catch(error => this.setState({ error, isLoading: false }));
    }



  render() {
    const { holdings, transactions, isLoading, follower_count,
        follow_status, daily_data_chart, daily_gain, account_name, current_balance} = this.state;
    return (
    <React.Fragment>
          <Grid container spacing={3}>

            <Grid item xs={12}>
                <Paper style={{ padding: "10px"}}>
                    <Grid container spacing={3} alignContent={"center"} alignItems={"center"}>
                        <Grid item xs={6} md={6} lg={3} >
                            <h2>Account Name:</h2>
                            <h3>{account_name}</h3>
                        </Grid>
                        <Grid item xs={6} md={6} lg={3} >
                            <h2>Current Balance:</h2>
                            <h3>
                                <CurrencyFormat value={current_balance}
                                    displayType={'text'}
                                    thousandSeparator={true}
                                    decimalScale={2}
                                    prefix={'$'} />
                            </h3>
                        </Grid>
                        <Grid item xs={6} md={6} lg={3}>
                            <h2>Followers:</h2>
                            <h3>{follower_count}</h3>
                        </Grid>
                        <Grid item xs={6} md={6} lg={3}>
                        { follow_status ? <Button onClick={this.unfollow} variant={"contained"} color={"secondary"}>Unfollow</Button>
                            : <Button onClick={this.follow} variant={"contained"} color={"primary"}>Follow</Button>}
                        </Grid>
                    </Grid>
                </Paper>
            </Grid>
            {/* Chart */}
            <Grid item xs={12} md={12} lg={6}>
              <Paper style={{ padding: "10px", display: 'flex', overflow: 'auto', flexDirection: 'column', height: "240px" }}>
                <Chart chartdata={daily_data_chart} daily_gain={daily_gain} current_balance={current_balance}/>
              </Paper>
            </Grid>
            {/* Recent Transactions */}
            <Grid item xs={12} md={12} lg={6}>
              <Paper style={{ display: 'flex', overflow: 'auto', flexDirection: 'column', height: "240px" }}>
                <Deposits transactions={transactions}/>
              </Paper>
            </Grid>
            {/* Portfolio table */}
            <Grid item xs={12}>
              <Title>Portfolio Holdings</Title>
              <TableContainer component={Paper}>
                <Orders my_hold={holdings}/>
              </TableContainer>
            </Grid>
          </Grid>
      </React.Fragment>
        )
  }
}

export default Dashboard;