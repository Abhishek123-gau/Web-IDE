import BuySellOptionsList from './BuySellOptionsList';

const MainContent = ({ className }) => {
  return (
    <div className={`w-full p-6 bg-white rounded-2xl shadow-xl ${className}`}>
      <h1 className="text-3xl font-bold mb-4">Buy/Sell Options</h1>
      <BuySellOptionsList />
    </div>
  );
};

export default MainContent;