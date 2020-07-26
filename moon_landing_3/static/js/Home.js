import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem"
import ListItemText from "@material-ui/core/ListItemText";
import ListItemIcon from "@material-ui/core/ListItemIcon";
import Button from "@material-ui/core/Button";
import AddIcon from '@material-ui/icons/Add';
import ListSubheader from "@material-ui/core/ListSubheader"

const useStyles = makeStyles((theme) => ({
  root: {
    width: '100%',
    maxWidth: 360,
    backgroundColor: theme.palette.background.paper,
  },
}));


function ListItemLink(props) {
  return <ListItem button component="a" {...props} />;
}

class AccountsList extends React.Component {

      constructor() {
        super();
          this.state = {
            isLoading: true,
            accounts: []
          }
      }

    componentDidMount() {
        // Where we're fetching data from
      fetch(`/home_accounts`)
        // We get the API response and receive data in JSON format...
        .then(response => response.json())
        // ...then we update the users state
        .then(data =>
          this.setState({
            accounts: data['accounts'],
            isLoading: false,
          })
        )
        // Catch any errors we hit and update the app
        .catch(error => this.setState({ error, isLoading: false }));
    }

    render() {
        const { accounts } = this.state;
        var elements = [];
        for(var i=0;i<accounts.length;i++){
            elements.push(
                <ListItem button key={i}>
                  <ListItemIcon>
                  </ListItemIcon>
                  <ListItemText primary={accounts[i]['account_name']} secondary={accounts[i]['balance']} />
                </ListItem>
            );
        }
        return (
            <div>
            {elements}
            </div>
        );
    }
}

export default function Home() {
    const classes = useStyles();

    return (
        <React.Fragment>
        <h1> Connect your Trading Accounts Below</h1>
        <Button variant="contained" color="primary" aria-label="add" onClick={e => window.location.href = '/auth/td-ameritrade/'}>
          <AddIcon />
          TD Ameritrade
        </Button>
        <div className={classes.root} style={{margin: "20px"}}>

          <List component="nav" aria-label="main mailbox folders">
              <ListSubheader>Connected Accounts</ListSubheader>
              <AccountsList/>
          </List>
        </div>
        </React.Fragment>
        )
}

