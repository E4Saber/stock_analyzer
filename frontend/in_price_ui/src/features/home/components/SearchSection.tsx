import React from 'react';
import { Input, Tag } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import './SearchSection.css';

const { Search } = Input;

interface SearchSectionProps {
  hotSearchTags: string[];
}

const SearchSection: React.FC<SearchSectionProps> = ({ hotSearchTags }) => {
  return (
    <section className="search-section">
      <div className="search-box">
        <div className="search-input-container">
          <Search 
            placeholder="输入股票名称、代码或关键词" 
            enterButton={<><SearchOutlined /> 搜索</>}
            size="large"
          />
        </div>
        
        <div className="hot-search">
          <span className="hot-search-label">热门搜索:</span>
          {hotSearchTags.map((tag, index) => (
            <Tag 
              key={index} 
              className="hot-tag"
            >
              {tag}
            </Tag>
          ))}
        </div>
      </div>
    </section>
  );
};

export default SearchSection;