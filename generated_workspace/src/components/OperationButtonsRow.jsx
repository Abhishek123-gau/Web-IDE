import React from 'react';
import Button from './Button';

const OperationButtonsRow = ({ onOperatorClick }) => (
  <div className="grid grid-cols-4 gap-3 p-2 bg-white rounded-2xl shadow-inner mt-4">
    <Button variant="secondary" className="text-xl pb-3" onClick={() => onOperatorClick('+')}>+</Button>
    <Button variant="secondary" className="text-xl pb-3" onClick={() => onOperatorClick('-')}>-</Button>
    <Button variant="secondary" className="text-xl pb-3" onClick={() => onOperatorClick('*')}>×</Button>
    <Button variant="secondary" className="text-xl pb-3" onClick={() => onOperatorClick('/')}>÷</Button>
    <Button variant="tertiary" className="col-span-4 text-red-500 hover:bg-red-50" onClick={() => onOperatorClick('C')}>Clear</Button>
  </div>
);

export default OperationButtonsRow;