import React from 'react';
import { PlaidLink } from 'react-plaid-link';
import axios from 'axios';
import Cookies from 'js-cookie'

function createAccount(token, metadata) {
    const csrftoken = Cookies.get('csrftoken');
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

  const onExit = () => console.log('onExit');
  const onEvent = () => console.log('onEvent');
  const onSuccess = (token, metadata) => createAccount(token, metadata);



  return (
      <PlaidLink
        className="CustomButton"
        style={{ padding: '20px', fontSize: '16px', cursor: 'pointer', background: '#3f51b5', color: 'white' }}
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