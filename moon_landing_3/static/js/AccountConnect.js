import React from 'react';
import { PlaidLink } from 'react-plaid-link';
import axios from 'axios';
import Cookies from 'js-cookie'

function createAccount(token, metadata) {
    const csrftoken = Cookies.get('csrftoken');
    console.log(token, metadata);
    axios.post('/account_creation',
      {
        token: token,
        metadata: metadata
        },
       {
           headers: {
            'X-CSRFToken': csrftoken
           }
      });

}

const AccountConnect = props => {

  const onExit = (error, metadata) => console.log('onExit', error, metadata);
  const onEvent = (eventName, metadata) => console.log('onEvent', eventName, metadata);
  const onSuccess = (token, metadata) => createAccount(token, metadata);



  return (
      <PlaidLink
        className="CustomButton"
        style={{ padding: '20px', fontSize: '16px', cursor: 'pointer' }}
        token={props.token}
        onExit={onExit}
        onSuccess={onSuccess}
        onEvent={onEvent}
        env="development"
      >
        Click to Connect Brokerage Account
      </PlaidLink>
  );
};
export default AccountConnect;