import React, {useEffect, useState} from 'react';
import { makeStyles } from '@material-ui/core/styles';
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem"
import Grid from "@material-ui/core/Grid";
import Paper from "@material-ui/core/Paper";
import ListSubheader from "@material-ui/core/ListSubheader";
import AccountConnect from "./AccountConnect";
import AccountList from "./AccountList";
import Button from "@material-ui/core/Button";
import TextField from "@material-ui/core/TextField";
import axios from 'axios';
import Cookies from "js-cookie";
import Deposits from "./Deposits";

const useStyles = makeStyles((theme) => ({
  root: {
    width: '100%',
    maxWidth: 360,
    backgroundColor: theme.palette.background.paper,
  },
  paper: {
    padding: theme.spacing(2),
    display: 'flex',
    overflow: 'auto',
    flexDirection: 'column',
  },
}));


function ListItemLink(props) {
  return <ListItem button component="a" {...props} />;
}


export default function Home() {
    const classes = useStyles();
    const [token, setToken] = useState('');
    const [accounts, setAccounts] = useState([]);
    const [followedaccounts, setFollowedaccounts] = useState([]);
    const[username, setUsername] = useState('');
    const[uniquefollowers, setUniquefollowers] = useState(0);
    const [newusername, setNewusername] = useState(username);
    const [followed_transactions, setFollowedTransactions] = useState([]);

    useEffect(() => {
        axios.get('/plaid/token').then(response => setToken(response['data']));

    }, []);

    useEffect(() => {
      fetch(`/followed_transactions`)
        .then(response => response.json())
        .then(data =>{
            setFollowedTransactions(data['followed_transactions']);
        });
    }, []);



    useEffect(() => {
      fetch(`/home_accounts`)
        .then(response => response.json())
        .then(data =>{
            setAccounts(data['accounts']);
            setUsername(data['username']);
            setFollowedaccounts(data['followedaccounts']);
            setUniquefollowers(data['unique_followers']);
        });
    }, []);

    const handleSubmit = (evt) => {
      evt.preventDefault();
      const csrftoken = Cookies.get('csrftoken');
        const firebase_token = Cookies.get('token');  //the firebase token so we can change this users screen name
        axios.post('/change/username',
          {
            username: newusername,
            firebase_token: firebase_token
            },
           {
               headers: {
                'X-CSRFToken': csrftoken
               }
          }).then(response => setUsername(response['data']['username']));
    }

    return (
        <React.Fragment>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Paper className={classes.paper}>
                  <Grid container spacing={3} alignContent={"center"} alignItems={"center"}>
                      <Grid item xs={6} md={6} lg={6} >
                            <form onSubmit={handleSubmit}>
                            <TextField id="outlined-basic" label="Update Screename" variant="outlined"
                            value={newusername} onChange={e => setNewusername(e.target.value)}>
                              Update Your Username:
                            </TextField>
                            <Button
                                type="submit"
                                className={classes.button}
                                variant={"outlined"}
                            >
                                Update
                            </Button>
                          </form>
                            <h3>
                                {username}
                            </h3>
                      </Grid>
                      <Grid item xs={6} md={6} lg={6} >
                          <h2>Followers:</h2>
                          <h3>{uniquefollowers}</h3>
                      </Grid>
                  </Grid>
              </Paper>
            </Grid>
            <Grid item xs={12} md={12} lg={6}>
                <Paper className={classes.paper}>
                <AccountConnect token={token}/>
                  <List component="nav" aria-label="main mailbox folders">
                      <ListSubheader className={classes.root}>Your Accounts</ListSubheader>
                      <AccountList owned_accounts={true} accounts={accounts}/>
                  </List>
                </Paper>
            </Grid>
            <Grid item xs={12} md={12} lg={6}>
              <Paper className={classes.paper}>
                <h3>See your followed accounts below – News feed coming soon!</h3>
                <List component="nav" aria-label="main mailbox folders">
                      <ListSubheader className={classes.root}>Followed Accounts</ListSubheader>
                      <AccountList accounts={followedaccounts}/>
                  </List>
              </Paper>
            </Grid>
            <Grid item xs={12} md={12} lg={12}>
              <Paper style={{ display: 'flex', overflow: 'auto', flexDirection: 'column', height: "240px" }}>
                <Deposits transactions={followed_transactions} title={'Trades from Followed Accounts'} account_name={true}/>
              </Paper>
            </Grid>
          </Grid>
        </React.Fragment>
    )
}

