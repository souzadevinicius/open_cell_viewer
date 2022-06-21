(function() {

  'use strict';

  var trainControllers = angular.module('predictControllers', []);
  trainControllers.controller('PredictCtrl', [
    '$scope', '$http',
    function($scope, $http) {
      var vm = this;
      vm.uploadTrainFile = function() {
        if (_.isEmpty($scope.train) || _.isEmpty(vm.categoryName))
          return;
        upload('/train/images?cm=' + vm.cm + '&n=' + vm.categoryName, 'train[]', $scope.train, function(data) {
          $scope.load(true);
          vm.getTrainedImages(true, vm.categoryName);
          vm.retrain();
          vm.trainedType = vm.categoryName;
          vm.categoryName = _.isEmpty(vm.cm) ? '' : vm.categoryName;
        })
      }

      vm.uploadPredictFile = function() {
        if (_.isEmpty($scope.predict))
          return;
        upload('/predict?cm=' + vm.cm, 'predict[]', $scope.predict, function(data) {
          alert(data)
        })
      }

      function upload(url, elementName, scopeElement, cbSuccess, cbError) {
        if (!window.FormData)
          throw new Error('Unsupported browser version');
        var form = new window.FormData();
        for (var index = 0, len = scopeElement.length; index < len; index++) {
          var element = scopeElement[index];
          form.append(elementName, element);
        }
        scopeElement = [];
        $http.post(url, form, {
          transformRequest: angular.identity,
          headers: { 'Content-Type': undefined },
        }).success(cbSuccess);
        return;
      }

      vm.retrain = function() {
        $http.post('/train').success(function(data) {
          $scope.load(false);
        })
      }

      vm.getTrainedImages = function(forceReload, predtype) {
        //Atualiza selects
        var refresh = function(data, predtype) {
            vm.trainedData = data;
            vm.trainedTypes = _.chain(data)
              .map(function(stooge) { return stooge.name.split('_')[0] })
              .uniq()
              .value();
            vm.trainedType = predtype || vm.trainedTypes[0]
            vm.trainImages = _.chain(data)
              .filter(function(d) { return d.name.split('_')[0] == vm.trainedType })
              .map(function(d) {
                d.path += '?d=' + new Date().getTime();
                return d
              })
              .value();
          }
          //SE JÁ TIVER OS DADOS DE TREINAMENTO E NÃO FOR CARREGAMENTO FORÇADO PEGA DO CACHE
        if (!_.isEmpty(vm.trainedTypes) && !forceReload) {
          refresh(vm.trainedData, predtype)
          return;
        }

        $http.get('/train/thumb').success(function(data) {
          refresh(data, predtype)
        })
      }

      vm.getTrainedImages(true);
    }
  ]);
})();
