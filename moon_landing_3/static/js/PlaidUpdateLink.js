import React, {useEffect, useState} from 'react';
import { PlaidLink } from 'react-plaid-link';
import axios from 'axios';
import Cookies from 'js-cookie'

function createAccount(token, metadata) {
    const csrftoken = Cookies.get('csrftoken');
    axios.post('/account_creation',
      {
        token: token,
        metadata: metadata,
        is_update: true
        },
       {
           headers: {
            'X-CSRFToken': csrftoken
           }
      });

}

const PlaidUpdateLink = props => {

  const onExit = () => console.log('onExit');
  const onEvent = () => console.log('onEvent');
  const onSuccess = (token, metadata) => createAccount(token, metadata);
  const [token, setToken] = useState('');

    useEffect(() => {
        axios.get('/plaid/token?item_id='+props.item_id).then(response => setToken(response['data']));
    }, []);

  return (
      <PlaidLink
        className="CustomButton"
        style={{ padding: '20px', fontSize: '16px', cursor: 'pointer', background: '#f50057', color: 'white' }}
        token={token}
        onExit={onExit}
        onSuccess={onSuccess}
        onEvent={onEvent}
        env="development"
      >
        Update
      </PlaidLink>
  );
};
export default PlaidUpdateLink;