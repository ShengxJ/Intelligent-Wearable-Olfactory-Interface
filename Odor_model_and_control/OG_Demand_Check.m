function demand_check = OG_Demand_Check(user_track,OG_pos,range_,OG_dt)
%OG_Demand_Check Function:
%       compare the orientation of user's head, position, and velocity with
%       the estimated 5-ppm boundaries of odor emmisions at the height of 
%       user's nose. OG_dt considering both the harware response time and 
%       odor emmision time from OG the user's nose. 
% Author:
%       JIA Shengxin 2023
x=user_track(:,1);y=user_track(:,2);
Head_vec=user_track(:,4:6);velocity=user_track(:,7:9);
plane_dist = [x-OG_pos(1),y-OG_pos(2)];
contourpoints=points_in_contour(range_,plane_dist(:,1),plane_dist(:,2));
u = zeros(3,length(velocity)); v = zeros(3,length(plane_dist));
u(1:2,:) = velocity(:,1:2)';v(1:2,:) = -plane_dist';
vectowardsOG= atan2(vecnorm(cross(u,v)),dot(u,v));
vec2OG = cos(vectowardsOG).*vecnorm(velocity(:,1:2)');
check_dist = (vecnorm(contourpoints)+vec2OG.*OG_dt)-vecnorm(plane_dist');
demand_check=find(check_dist>=0);
u = zeros(3,length(Head_vec)); v = zeros(3,length(plane_dist));
u(1:2,:) = Head_vec(:,1:2)';v(1:2,:) = -plane_dist';
angletowardsOG= atan2(vecnorm(cross(u,v)),dot(u,v)); %head vector towards odor
demand_check_angle = find((angletowardsOG>1/4*pi)+(angletowardsOG<-1/4*pi)>=1);
head_vec_check = ismember(demand_check,demand_check_angle);
if head_vec_check 
    demand_check(head_vec_check==1)=[];
end
end
function contourpoints=points_in_contour(contour,X,Y)
%contour size: 2xN
contourpoints=zeros(2,length(X));
contour_xmin = min(contour(1,:));
contour_xmax = max(contour(1,:));
X_list = find((X>=contour_xmin) == (X<=contour_xmax));
for i = 1:length(X_list)
    id = X_list(i);
    idxs = find(abs(contour(1,:)-X(id))<=0.01);
    [~,idx] = min(abs(contour(2,idxs)-Y(id)));
    contourpoints(:,id) = contour(:,idxs(idx));
end
end