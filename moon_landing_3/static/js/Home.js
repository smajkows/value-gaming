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
    const[username, setUsername] = useState('');
    const [newusername, setNewusername] = useState(username);

    useEffect(() => {
        axios.get('/plaid/token').then(response => setToken(response['data']));
    }, []);

    useEffect(() => {
      fetch(`/home_accounts`)
        .then(response => response.json())
        .then(data =>{
            setAccounts(data['accounts']);
            setUsername(data['username']);
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
                <div>
                  <form onSubmit={handleSubmit}>
                    <TextField id="outlined-basic" label="Update Screename" variant="outlined"
                    value={newusername} onChange={e => setNewusername(e.target.value)}>
                      Update Your Username:
                    </TextField>
                    <Button
                        type="submit"
                        className={classes.button}
                    >
                        Update
                    </Button>
                  </form>
                <p>
                    {username}
                </p>
                </div>
              </Paper>
            </Grid>
            <Grid item xs={6}>
                <AccountConnect token={token}/>
                <div className={classes.root} style={{margin: "20px"}}>
                  <List component="nav" aria-label="main mailbox folders">
                      <ListSubheader className={classes.root}>Connected Accounts</ListSubheader>
                      <AccountList accounts={accounts}/>
                  </List>
                </div>
            </Grid>
            <Grid item xs={6}>
              <Paper className={classes.paper}>News Feed for Followed accounts coming soon!</Paper>
            </Grid>
          </Grid>
        </React.Fragment>
    )
}

