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
import CurrencyFormat from "react-currency-format";
import ListItemText from "@material-ui/core/ListItemText";
import ListItemIcon from "@material-ui/core/ListItemIcon";
import Modal from "@material-ui/core/Modal";

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
  modal_paper: {
    position: 'absolute',
    width: 400,
    backgroundColor: theme.palette.background.paper,
    border: '2px solid #000',
    boxShadow: theme.shadows[5],
    padding: theme.spacing(2, 4, 3),
  },
}));

function getModalStyle() {
  const top = 50;
  const left = 50;

  return {
    top: `${top}%`,
    left: `${left}%`,
    transform: `translate(-${top}%, -${left}%)`,
  };
}


export default function Settings() {
    const classes = useStyles();
    const [modalStyle] = React.useState(getModalStyle);
    const [open, setOpen] = React.useState(false);
    const [token, setToken] = useState('');
    const [plans, setPlans] = useState([]);
    const [currPlan, setCurrPlan] = useState(null);
    const [subscription, setSubscription] = useState(null);

      const handleOpen = () => {
        setOpen(true);
      };

      const handleClose = () => {
        setOpen(false);
      };


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
            addPaymentMethod(payload.nonce).done(function(xhr){
            }).fail(function (xhr) {
                console.log('FAIL');
            });
          });
        });
    });

    useEffect(() => {
      fetch(`/settings_json`)
        .then(response => response.json())
        .then(data =>{
            setPlans(data['available_plans']);
            setCurrPlan(data['current_plan']);
            setSubscription(data['subscription']);
        });
    }, []);


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

      function upgrade(plan_id) {
        const firebase_token = Cookies.get('token');  //the firebase token so we can change this users screen name
        const csrftoken = Cookies.get('csrftoken');

        console.log('upgrade request sent ' + plan_id);
        axios.post('/update_user_plan',
          {
            firebase_token: firebase_token,
            plan_id: plan_id
            },
           {
               headers: {
                'X-CSRFToken': csrftoken
               }
          }).then(response => {
              setCurrPlan(response['data']['current_user_plan']);
              setSubscription(response['data']['subscription']);
              handleClose();
        });
    }



    return (
        <React.Fragment>
          <Grid container spacing={3}>
            <Grid item xs={12} md={12} lg={6}>
              <Paper className={classes.paper}>
                  <Grid container spacing={3} alignContent={"center"} alignItems={"center"}>
                      <Grid item xs={12}>
                        <div id="dropin-container"></div>
                        <Button type="submit" id="submit-button">Add Payment Method</Button>
                      </Grid>
                  </Grid>
              </Paper>
            </Grid>
            <Grid item xs={12} md={12} lg={6}>
                <Paper className={classes.paper}>
                  <List component="nav" aria-label="main mailbox folders">
                      <ListSubheader className={classes.root}>Available Plans</ListSubheader>
                        {plans.map((item, key) => (
                          <ListItem key={key}>
                          {currPlan ?
                                <ListItemIcon style={{margin:'10px'}}>
                                    {currPlan['id'] == item['id'] ? (<h3 style={{color: "green"}}>Subscribed</h3>) :
                                        (
                                            <div>
                                              <Button type="button" onClick={handleOpen}>
                                                Switch?
                                              </Button>
                                              <Modal
                                                open={open}
                                                onClose={handleClose}
                                                aria-labelledby="simple-modal-title"
                                                aria-describedby="simple-modal-description"
                                              >
                                              <div style={modalStyle} className={classes.modal_paper}>
                                                  <h2 id="simple-modal-title">Awesome, confirm you'd like to swtich plans below!</h2>
                                                  <p id="simple-modal-description">
                                                      You will be charged ${item.price} immdediatly upon confirmation.
                                                      You will now be able to follow {item.followers_allowed} accounts!
                                                  </p>
                                                  {subscription ? <p>Confirming switch will <strong> cancel </strong>
                                                      your existing plan: {currPlan.name}
                                                  </p> : <p></p>}
                                                  <Button onClick={() => upgrade(item['id'])}> Confirm </Button>
                                                </div>
                                              </Modal>
                                            </div>
                                        )}
                                </ListItemIcon> : <ListItemIcon></ListItemIcon>
                            }
                            <ListItemText primary={item.name}
                                secondary={<CurrencyFormat value={item.price} displayType={'text'}
                                                           thousandSeparator={true}
                                                           prefix={item.description + '  $'} suffix={'/mo'} decimalScale={2}/>}/>
                          </ListItem>
                      ))}
                  </List>
                </Paper>
            </Grid>
          </Grid>
        </React.Fragment>
    )
}

