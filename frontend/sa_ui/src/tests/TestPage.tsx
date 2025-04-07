import React from 'react';
import { SupplyChainModal } from './demo1'; // 确保路径正确
import { Button } from 'antd';
import { useState } from 'react';
import ExamplePage from './demo3'; // 确保路径正确

const TestPage = () => {
    const [visible, setVisible] = useState(false);
  
    return (
      <>
        {/* <Button onClick={() => setVisible(true)}>查看供应链</Button>
        
        <SupplyChainModal 
          visible={visible} 
          onClose={() => setVisible(false)} 
          title="XX公司供应链关系图"
        /> */}

        <ExamplePage />
      </>
    );
}

export default TestPage;