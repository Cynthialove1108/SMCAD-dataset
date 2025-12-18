"""
Feature labeling system for assembly dataset
装配特征数据集的标注系统
"""

from OCC.Extend.TopologyUtils import TopologyExplorer
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse


class FeatureLabel:
    """特征标注类"""
    def __init__(self):
        self.face_label_map = {}  # {face: label_info}
        self.feature_list = []  # 特征列表

    def add_feature(self, feature, feature_id):
        """
        添加特征及其标签
        Args:
            feature: 特征对象(AssemblyFeature实例)
            feature_id: 特征ID
        """
        self.feature_list.append({
            'id': feature_id,
            'type': feature.get_type(),
            'parameters': feature.get_parameters(),
            'shape': feature.get_shape()
        })

    def label_faces(self, combined_shape, base_shape, feature_shapes_with_labels):
        """
        为组合体的每个面标注特征类型
        Args:
            combined_shape: 组合后的完整形状
            base_shape: 基体形状
            feature_shapes_with_labels: [(feature_shape, feature_type, feature_id), ...]
        Returns:
            dict: {face: label_string}
        """
        explorer = TopologyExplorer(combined_shape)
        all_faces = list(explorer.faces())

        # 标注基体面
        base_explorer = TopologyExplorer(base_shape)
        base_faces = set(base_explorer.faces())

        for face in all_faces:
            # 默认标签为基体
            self.face_label_map[face] = "base_part"

        # 标注特征面
        for feature_shape, feature_type, feature_id in feature_shapes_with_labels:
            feature_explorer = TopologyExplorer(feature_shape)
            feature_faces = list(feature_explorer.faces())

            for face in all_faces:
                # 检查面是否属于该特征
                # 简化处理:通过布尔运算判断面是否在特征形状内
                for f_face in feature_faces:
                    if self._faces_are_similar(face, f_face):
                        # 格式: feature_type_id (如 threaded_hole_1)
                        self.face_label_map[face] = f"{feature_type}_{feature_id}"
                        break

        return self.face_label_map

    def _faces_are_similar(self, face1, face2, tolerance=1e-6):
        """
        判断两个面是否相似(简化判断)
        实际应用中可使用更精确的几何比较
        """
        # 这里使用简化的判断方法
        # 在实际应用中,应该使用更严格的几何比较
        try:
            from OCC.Core.BRepGProp import brepgprop_SurfaceProperties
            from OCC.Core.GProp import GProp_GProps

            props1 = GProp_GProps()
            props2 = GProp_GProps()
            brepgprop_SurfaceProperties(face1, props1)
            brepgprop_SurfaceProperties(face2, props2)

            mass1 = props1.Mass()
            mass2 = props2.Mass()

            cog1 = props1.CentreOfMass()
            cog2 = props2.CentreOfMass()

            # 比较面积和质心
            area_similar = abs(mass1 - mass2) < tolerance
            cog_dist = cog1.Distance(cog2)
            cog_similar = cog_dist < tolerance

            return area_similar and cog_similar
        except:
            return False

    def generate_label_map_simple(self, combined_shape, base_type, feature_list):
        """
        简化的标注方法
        Args:
            combined_shape: 组合后的形状
            base_type: 基体类型
            feature_list: [(feature_type, feature_id), ...]
        Returns:
            dict: {face: label}
        """
        explorer = TopologyExplorer(combined_shape)
        all_faces = list(explorer.faces())

        # 为每个面分配ID和类型
        face_labels = {}
        for idx, face in enumerate(all_faces):
            # 简化标注:使用面索引
            # 格式: base_part 或 feature_type_feature_id_face_idx
            if len(feature_list) == 0:
                face_labels[face] = f"base_{base_type}"
            else:
                # 随机分配特征标签(实际应用中需要更精确的判断)
                # 这里采用启发式方法:前N个面为基体,后续为特征
                if idx < len(all_faces) // 2:
                    face_labels[face] = f"base_{base_type}"
                else:
                    if feature_list:
                        feat_idx = idx % len(feature_list)
                        feat_type, feat_id = feature_list[feat_idx]
                        face_labels[face] = f"{feat_type}_{feat_id}"
                    else:
                        face_labels[face] = f"base_{base_type}"

        return face_labels


class FeatureLabelGenerator:
    """特征标签生成器"""
    def __init__(self, base_part, features):
        """
        Args:
            base_part: 基体零件对象
            features: 特征列表 [(feature_obj, operation), ...]
                     operation: 'cut' 或 'fuse'
        """
        self.base_part = base_part
        self.features = features
        self.label_map = {}

    def generate_labels(self, combined_shape):
        """
        生成特征标签映射
        Args:
            combined_shape: 组合后的形状
        Returns:
            dict: {face: label}
        """
        labeler = FeatureLabel()

        # 收集特征信息
        feature_info_list = []
        for idx, (feature, operation) in enumerate(self.features):
            feature_info_list.append((feature.get_type(), idx))

        # 生成标签
        self.label_map = labeler.generate_label_map_simple(
            combined_shape,
            self.base_part.part_type,
            feature_info_list
        )

        return self.label_map

    def get_label_statistics(self):
        """获取标签统计信息"""
        label_counts = {}
        for label in self.label_map.values():
            # 提取特征类型(去掉ID后缀)
            if '_' in label:
                parts = label.split('_')
                if len(parts) >= 2:
                    feature_type = '_'.join(parts[:-1])  # 去掉最后的ID
                else:
                    feature_type = label
            else:
                feature_type = label

            if feature_type in label_counts:
                label_counts[feature_type] += 1
            else:
                label_counts[feature_type] = 1

        return label_counts

    def export_labels_to_dict(self):
        """
        导出标签为字典格式
        Returns:
            dict: 标签映射
        """
        return self.label_map
