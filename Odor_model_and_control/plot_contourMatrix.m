function  plot_contourMatrix(ax,M,z_,x_,y_,theta,cmap_max,cmap_min,cmap)
%plot_contourMatrix  Function:
%       Plot contour matrix in 3D space
% Author:
%       JIA Shengxin 2023
i = 1;
z=M(1,1);N = M(2,1);index = N+1;X_ = M(1,2:index);Y_ = M(2,2:index);Z=zeros(size(X_));
color_idx = round((z-cmap_min)/(cmap_max-cmap_min)*256);
if color_idx>256
    color_idx=256;
end
X=X_*cos(theta)-Y_*sin(theta);Y=X_*sin(theta)+Y_*cos(theta);
X=X+x_;Y=Y+y_;Z=Z+z_;
line_color=cmap(color_idx,:);
plot3(ax,X,Y,Z,'Color',line_color','LineStyle',':','LineWidth',z/30);
while index<length(M)-i
    i=i+1;
    z = M(1,index+1);N=M(2,index+1);index_=index+N+1;
    X_ = M(1,index+2:index_);Y_ = M(2,index+2:index_);Z=zeros(size(X_));
    X=X_*cos(theta)-Y_*sin(theta);Y=X_*sin(theta)+Y_*cos(theta);
    X=X+x_;Y=Y+y_;Z=Z+z_;
    color_idx = round((z-cmap_min)/(cmap_max-cmap_min)*256);
    if color_idx>256
        color_idx=256;
    end
    line_color=cmap(color_idx,:);    
    plot3(X,Y,Z,'Color',line_color','LineStyle',':','LineWidth',z/30);
    index=index_;
    view(-30, 30)
    axis equal
end
end