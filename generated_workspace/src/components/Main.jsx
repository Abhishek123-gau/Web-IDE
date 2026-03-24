import ProfilePicture from './ProfilePicture';
import BioData from './BioData';

const Main = ({ profilePicSrc, bioData }) => {
  return (
    <div className="flex flex-col items-center p-6 bg-white rounded-2xl shadow-xl hover:scale-105 transition-all">
      <ProfilePicture src={profilePicSrc} />
      <BioData data={bioData} />
    </div>
  );
};

export default Main;