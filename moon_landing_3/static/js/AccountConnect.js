import React from 'react';
import { PlaidLink } from 'react-plaid-link';

const AccountConnect = props => {
  const onExit = (error, metadata) => console.log('onExit', error, metadata);
  const onEvent = (eventName, metadata) => console.log('onEvent', eventName, metadata);
  const onSuccess = (token, metadata) =>
    console.log('onSuccess', token, metadata);



  return (
      <PlaidLink
        className="CustomButton"
        style={{ padding: '20px', fontSize: '16px', cursor: 'pointer' }}
        token={props.token}
        onExit={onExit}
        onSuccess={onSuccess}
        onEvent={onEvent}
        env="sandbox"
      >
        Open Link and connect your bank!
      </PlaidLink>
  );
};
export default AccountConnect;