import React, {useEffect, useState} from 'react';
import Button from "@material-ui/core/Button";
import { makeStyles } from '@material-ui/core/styles';
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem"
import Grid from "@material-ui/core/Grid";
import Paper from "@material-ui/core/Paper";
import ListSubheader from "@material-ui/core/ListSubheader";
import axios from 'axios';
import Cookies from "js-cookie";
import braintree from 'braintree-web-drop-in'

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


export default function Settings() {
    const classes = useStyles();
    const [token, setToken] = useState('');


    useEffect(() => {
        axios.get('/braintree/token').then(response => setToken(response['data']));

    }, []);

    var addPaymentButton = document.getElementById('submit-button');

    braintree.create({
        authorization: token,
        container: '#dropin-container',
        }, function (createErr, instance) {
        addPaymentButton.addEventListener('click', function (event) {
          event.preventDefault();
          instance.requestPaymentMethod(function (err, payload) {
            if (err) {
              console.log('Error', err);
              return;
            }
            // Add the nonce to the form and submit
            console.log(payload.nonce);
            addPaymentMethod(payload.nonce).done(function(xhr){
                console.log('payment method added!');
            }).fail(function (xhr) {
                console.log('FAIL');
            });
          });
        });
    });


    function addPaymentMethod(paymentNonce) {
        const firebase_token = Cookies.get('token');  //the firebase token so we can change this users screen name
        const csrftoken = Cookies.get('csrftoken');
        axios.post('/add_payment_method',
          {
            payment_method_nonce: paymentNonce,
            firebase_token: firebase_token
            },
           {
               headers: {
                'X-CSRFToken': csrftoken
               }
          }).then(response => console.log('added payment method'));
    }

    return (
        <React.Fragment>
          <Grid container spacing={3}>
            <Grid item xs={12} md={12} lg={6}>
              <Paper className={classes.paper}>
                  <Grid container spacing={3} alignContent={"center"} alignItems={"center"}>
                      <Grid item xs={12}>
                        <div id="dropin-container"></div>
                        <Button class="payment-button" type="submit" id="submit-button">Add Payment Method</Button>
                      </Grid>
                  </Grid>
              </Paper>
            </Grid>
            <Grid item xs={12} md={12} lg={6}>
                <Paper className={classes.paper}>
                  <List component="nav" aria-label="main mailbox folders">
                      <ListSubheader className={classes.root}>Your Subscriptions</ListSubheader>
                  </List>
                </Paper>
            </Grid>
          </Grid>
        </React.Fragment>
    )
}

